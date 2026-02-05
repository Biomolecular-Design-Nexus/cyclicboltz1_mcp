#!/usr/bin/env python3
"""
Script: predict_affinity.py
Description: Predict binding affinity between cyclic peptide and protein target

Original Use Case: examples/use_case_3_cyclic_peptide_affinity.py
Dependencies Removed: None (was dependency-free)

IMPORTANT NOTE: This script is provided for completeness but may not work as expected.
Step 4 testing revealed that Boltz affinity prediction only supports small molecule ligands,
not peptide-peptide interactions. This script can be used as a template for future
ligand-protein affinity predictions.

Usage:
    python scripts/predict_affinity.py --peptide <sequence> --target <sequence> --output <output_dir>

Example:
    python scripts/predict_affinity.py --peptide "QLEDSEVEAVAKG" --target "MKLLVASILALAVCSGSAKETTVLTLSDQGKFSL" --output results/affinity
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import subprocess
import tempfile
import yaml
import json
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "model": "boltz2",  # Affinity prediction requires Boltz-2
    "accelerator": "cpu",
    "diffusion_samples": 5,
    "diffusion_samples_affinity": 5,
    "recycling_steps": 3,
    "use_msa_server": True,
    "validate_sequences": True,
    "target_chain_id": "A",
    "peptide_chain_id": "B"
}

# ==============================================================================
# Utility Functions (inlined from use case)
# ==============================================================================
def validate_amino_acid_sequence(sequence: str) -> bool:
    """Validate amino acid sequence contains only standard residues."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    return all(aa in valid_aa for aa in sequence.upper())

def create_peptide_target_config(
    peptide_seq: str,
    target_seq: str,
    target_chain_id: str = "A",
    peptide_chain_id: str = "B",
    use_msa_server: bool = True
) -> Dict[str, Any]:
    """Create configuration dictionary for peptide-target affinity prediction."""
    config = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": target_chain_id,
                    "sequence": target_seq
                }
            },
            {
                "protein": {
                    "id": peptide_chain_id,
                    "sequence": peptide_seq,
                    "cyclic": True  # Mark the peptide as cyclic
                }
            }
        ],
        "properties": [
            {
                "affinity": {
                    "binder": peptide_chain_id  # The cyclic peptide is the binder
                }
            }
        ]
    }

    if not use_msa_server:
        config["sequences"][0]["protein"]["msa"] = "empty"
        config["sequences"][1]["protein"]["msa"] = "empty"

    return config

def save_yaml_config(config: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Save configuration to YAML file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def run_boltz_prediction(
    yaml_path: Union[str, Path],
    output_dir: Union[str, Path],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Run Boltz prediction using subprocess."""
    config = {**DEFAULT_CONFIG, **(config or {})}

    cmd = [
        "boltz", "predict", str(yaml_path),
        "--out_dir", str(output_dir),
        "--model", config["model"],
        "--accelerator", config["accelerator"],
        "--diffusion_samples", str(config["diffusion_samples"]),
        "--diffusion_samples_affinity", str(config["diffusion_samples_affinity"]),
        "--recycling_steps", str(config["recycling_steps"])
    ]

    if config["use_msa_server"]:
        cmd.append("--use_msa_server")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd)
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "command": " ".join(cmd),
            "error": str(e)
        }

def analyze_affinity_results(output_dir: Union[str, Path]) -> Dict[str, Any]:
    """Parse and analyze affinity prediction results."""
    pred_dir = Path(output_dir) / "predictions"
    affinity_files = list(pred_dir.rglob("affinity_*.json"))

    if not affinity_files:
        return {"affinity_files": 0, "analyses": []}

    analyses = []
    for affinity_file in affinity_files:
        try:
            with open(affinity_file, 'r') as f:
                affinity_data = json.load(f)

            analysis = {
                "file": str(affinity_file.name),
                "affinity_value": affinity_data.get('affinity_pred_value', None),
                "affinity_probability": affinity_data.get('affinity_probability_binary', None)
            }

            # Convert to IC50 and pIC50 if value is available
            if analysis["affinity_value"] is not None:
                affinity_value = analysis["affinity_value"]
                ic50_um = 10 ** affinity_value
                pic50 = (6 - affinity_value) * 1.364

                analysis["ic50_um"] = ic50_um
                analysis["pic50"] = pic50

                # Interpret binding strength
                if affinity_value < -1:
                    strength = "Very Strong (nanomolar)"
                elif affinity_value < 0:
                    strength = "Strong (sub-micromolar)"
                elif affinity_value < 1:
                    strength = "Moderate (micromolar)"
                else:
                    strength = "Weak (>10 μM)"
                analysis["binding_strength"] = strength

            analyses.append(analysis)

        except Exception as e:
            analyses.append({
                "file": str(affinity_file.name),
                "error": str(e)
            })

    return {
        "affinity_files": len(affinity_files),
        "analyses": analyses
    }

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_predict_affinity(
    peptide_sequence: str,
    target_sequence: str,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Predict binding affinity between cyclic peptide and protein target.

    WARNING: Step 4 testing revealed that Boltz affinity prediction only supports
    small molecule ligands, not peptide-peptide interactions. This function
    is provided for completeness but may fail with the error:
    "Chain B is not a ligand! Affinity is currently only supported for ligands."

    Args:
        peptide_sequence: Amino acid sequence of cyclic peptide
        target_sequence: Amino acid sequence of target protein
        output_dir: Directory to save prediction results (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result
            - output_dir: Path to output directory (if used)
            - metadata: Execution metadata

    Example:
        >>> result = run_predict_affinity("QLEDSEVEAVAKG", "MKLLVASILALAVCSGSAKETTVLTLSDQGKFSL")
        >>> print(result['success'])
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not peptide_sequence or not target_sequence:
        return {
            "success": False,
            "error": "Both peptide and target sequences are required",
            "result": None,
            "output_dir": None,
            "metadata": {"config": config}
        }

    # Clean sequences
    peptide_seq = peptide_sequence.strip().upper()
    target_seq = target_sequence.strip().upper()

    # Validate sequences if requested
    if config.get("validate_sequences", True):
        if not validate_amino_acid_sequence(peptide_seq):
            return {
                "success": False,
                "error": "Invalid peptide sequence. Please use standard single-letter codes.",
                "result": None,
                "output_dir": None,
                "metadata": {"peptide_seq": peptide_seq, "target_seq": target_seq, "config": config}
            }

        if not validate_amino_acid_sequence(target_seq):
            return {
                "success": False,
                "error": "Invalid target sequence. Please use standard single-letter codes.",
                "result": None,
                "output_dir": None,
                "metadata": {"peptide_seq": peptide_seq, "target_seq": target_seq, "config": config}
            }

    # Check peptide size (Boltz has limits for affinity prediction)
    if len(peptide_seq) > 50:
        print(f"Warning: Peptide sequence is quite long ({len(peptide_seq)} residues). Affinity prediction works best with smaller peptides.")

    # Setup output directory
    if output_dir is None:
        output_dir = f"./cyclic_affinity_prediction_{len(peptide_seq)}aa_vs_{len(target_seq)}aa"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create YAML configuration
    affinity_config = create_peptide_target_config(
        peptide_seq,
        target_seq,
        target_chain_id=config["target_chain_id"],
        peptide_chain_id=config["peptide_chain_id"],
        use_msa_server=config["use_msa_server"]
    )

    # Use temporary file for YAML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        save_yaml_config(affinity_config, yaml_path)

        # Run prediction
        result = run_boltz_prediction(yaml_path, output_path, config)

        # Analyze results if prediction succeeded
        affinity_analysis = {}
        if result["success"]:
            affinity_analysis = analyze_affinity_results(output_path)

        # Check for output files
        pred_dir = output_path / "predictions"
        output_files = []
        if pred_dir.exists():
            output_files = [str(f) for f in pred_dir.rglob("*") if f.is_file()]

        return {
            "success": result["success"],
            "result": result,
            "affinity_analysis": affinity_analysis,
            "output_dir": str(output_path),
            "output_files": output_files,
            "metadata": {
                "peptide_sequence": peptide_seq,
                "target_sequence": target_seq,
                "peptide_length": len(peptide_seq),
                "target_length": len(target_seq),
                "config": config,
                "yaml_config": affinity_config
            },
            "error": result.get("error") if not result["success"] else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "result": None,
            "output_dir": str(output_path) if output_dir else None,
            "metadata": {"peptide_seq": peptide_seq, "target_seq": target_seq, "config": config}
        }

    finally:
        # Clean up temporary file
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--peptide', '-p',
        required=True,
        help='Cyclic peptide amino acid sequence'
    )
    parser.add_argument(
        '--target', '-t',
        required=True,
        help='Target protein amino acid sequence'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory path'
    )
    parser.add_argument(
        '--config',
        help='Config file (JSON/YAML)'
    )
    parser.add_argument(
        '--no-msa-server',
        action="store_true",
        help='Disable MSA server usage'
    )
    parser.add_argument(
        '--samples',
        type=int,
        help='Number of diffusion samples'
    )

    args = parser.parse_args()

    # Print warning about known limitation
    print("⚠️  WARNING: Step 4 testing revealed that Boltz affinity prediction")
    print("   only supports small molecule ligands, not peptide-peptide interactions.")
    print("   This script may fail with the error:")
    print("   'Chain B is not a ligand! Affinity is currently only supported for ligands.'")
    print("   Use this script as a template for ligand-protein affinity predictions.\n")

    # Load config if provided
    config = {}
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            if config_path.suffix.lower() == '.json':
                import json
                with open(config_path) as f:
                    config = json.load(f)
            else:
                with open(config_path) as f:
                    config = yaml.safe_load(f)

    # Override config with CLI args
    if args.no_msa_server:
        config["use_msa_server"] = False
    if args.samples:
        config["diffusion_samples"] = args.samples

    # Run
    result = run_predict_affinity(
        peptide_sequence=args.peptide,
        target_sequence=args.target,
        output_dir=args.output,
        config=config
    )

    if result["success"]:
        print(f"Success: Affinity prediction completed")
        print(f"Output directory: {result['output_dir']}")
        if result["affinity_analysis"]["affinity_files"] > 0:
            print(f"Affinity files: {result['affinity_analysis']['affinity_files']}")
            for analysis in result["affinity_analysis"]["analyses"]:
                if "error" not in analysis:
                    print(f"  Affinity value: {analysis.get('affinity_value', 'N/A')}")
                    print(f"  Binding strength: {analysis.get('binding_strength', 'N/A')}")
        if result["output_files"]:
            print(f"Generated {len(result['output_files'])} files")
        return 0
    else:
        print(f"Error: {result['error']}")
        return 1

if __name__ == '__main__':
    exit(main())