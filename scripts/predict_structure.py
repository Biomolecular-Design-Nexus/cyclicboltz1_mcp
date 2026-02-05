#!/usr/bin/env python3
"""
Script: predict_structure.py
Description: Predict 3D structure of cyclic peptide from sequence

Original Use Case: examples/use_case_1_cyclic_peptide_structure.py
Dependencies Removed: None (was dependency-free)

Usage:
    python scripts/predict_structure.py --input <sequence> --output <output_dir>

Example:
    python scripts/predict_structure.py --input "QLEDSEVEAVAKG" --output results/structure
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "model": "boltz1",
    "accelerator": "cpu",
    "diffusion_samples": 1,
    "recycling_steps": 3,
    "use_msa_server": True,
    "validate_sequence": True
}

# ==============================================================================
# Utility Functions (inlined from use case)
# ==============================================================================
def validate_amino_acid_sequence(sequence: str) -> bool:
    """Validate amino acid sequence contains only standard residues."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    return all(aa in valid_aa for aa in sequence.upper())

def create_cyclic_peptide_config(
    sequence: str,
    use_msa_server: bool = True,
    chain_id: str = "A"
) -> Dict[str, Any]:
    """Create configuration dictionary for cyclic peptide structure prediction."""
    config = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": chain_id,
                    "sequence": sequence,
                    "cyclic": True  # This is the key flag for cyclic peptides!
                }
            }
        ]
    }

    if not use_msa_server:
        config["sequences"][0]["protein"]["msa"] = "empty"

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

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_predict_structure(
    input_sequence: str,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Predict 3D structure of cyclic peptide from sequence.

    Args:
        input_sequence: Amino acid sequence of cyclic peptide
        output_dir: Directory to save prediction results (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result
            - output_dir: Path to output directory (if used)
            - metadata: Execution metadata

    Example:
        >>> result = run_predict_structure("QLEDSEVEAVAKG", "results/structure")
        >>> print(result['success'])
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_sequence or not input_sequence.strip():
        return {
            "success": False,
            "error": "Input sequence cannot be empty",
            "result": None,
            "output_dir": None,
            "metadata": {"config": config}
        }

    # Clean sequence
    sequence = input_sequence.strip().upper()

    # Validate sequence if requested
    if config.get("validate_sequence", True):
        if not validate_amino_acid_sequence(sequence):
            return {
                "success": False,
                "error": "Invalid amino acid sequence. Please use standard single-letter codes.",
                "result": None,
                "output_dir": None,
                "metadata": {"sequence": sequence, "config": config}
            }

    # Setup output directory
    if output_dir is None:
        output_dir = f"./cyclic_peptide_prediction_{len(sequence)}aa"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create YAML configuration
    peptide_config = create_cyclic_peptide_config(
        sequence,
        use_msa_server=config["use_msa_server"]
    )

    # Use temporary file for YAML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        save_yaml_config(peptide_config, yaml_path)

        # Run prediction
        result = run_boltz_prediction(yaml_path, output_path, config)

        # Check for output files
        pred_dir = output_path / "predictions"
        output_files = []
        if pred_dir.exists():
            output_files = [str(f) for f in pred_dir.rglob("*") if f.is_file()]

        return {
            "success": result["success"],
            "result": result,
            "output_dir": str(output_path),
            "output_files": output_files,
            "metadata": {
                "sequence": sequence,
                "sequence_length": len(sequence),
                "config": config,
                "yaml_config": peptide_config
            },
            "error": result.get("error") if not result["success"] else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "result": None,
            "output_dir": str(output_path) if output_dir else None,
            "metadata": {"sequence": sequence, "config": config}
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
        '--input', '-i',
        required=True,
        help='Cyclic peptide amino acid sequence'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory path'
    )
    parser.add_argument(
        '--config', '-c',
        help='Config file (JSON/YAML)'
    )
    parser.add_argument(
        '--model',
        choices=["boltz1", "boltz2"],
        help='Boltz model to use'
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
    if args.model:
        config["model"] = args.model
    if args.no_msa_server:
        config["use_msa_server"] = False
    if args.samples:
        config["diffusion_samples"] = args.samples

    # Run
    result = run_predict_structure(
        input_sequence=args.input,
        output_dir=args.output,
        config=config
    )

    if result["success"]:
        print(f"Success: Structure prediction completed")
        print(f"Output directory: {result['output_dir']}")
        if result["output_files"]:
            print(f"Generated {len(result['output_files'])} files")
        return 0
    else:
        print(f"Error: {result['error']}")
        return 1

if __name__ == '__main__':
    exit(main())