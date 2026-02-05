#!/usr/bin/env python3
"""
Script: predict_modified.py
Description: Predict structure of cyclic peptide with non-canonical amino acids

Original Use Case: examples/use_case_4_noncanonical_amino_acids.py
Dependencies Removed: None (was dependency-free)

Usage:
    python scripts/predict_modified.py --sequence <sequence> --modifications <mods> --output <output_dir>

Example:
    python scripts/predict_modified.py --sequence "QLEDSEVEAVAKG" --modifications "3:phosphoserine,7:hydroxyproline" --output results/modified
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
    "model": "boltz2",  # Recommended for modifications
    "accelerator": "cpu",
    "diffusion_samples": 2,
    "recycling_steps": 5,
    "use_msa_server": True,
    "validate_sequence": True,
    "chain_id": "A"
}

# Mapping of common modification names to CCD codes
MODIFICATION_MAP = {
    # Common modified amino acids
    "phosphoserine": "SEP",
    "phosphothreonine": "TPO",
    "phosphotyrosine": "PTR",
    "hydroxyproline": "HYP",
    "pyroglutamate": "PCA",
    "citrulline": "CIR",
    "ornithine": "ORN",
    "norleucine": "NLE",
    "aminobutyric": "ABA",
    "selenocysteine": "SEC",
    "selenomethionine": "MSE",

    # D-amino acids (if supported)
    "d_alanine": "DAL",
    "d_valine": "DVA",
    "d_leucine": "DLE",
    "d_phenylalanine": "DPN",

    # Other modifications
    "methylated_lysine": "MLY",
    "acetylated_lysine": "ALY",
    "nitrotyrosine": "NIY",
}

# ==============================================================================
# Utility Functions (inlined from use case)
# ==============================================================================
def validate_amino_acid_sequence(sequence: str) -> bool:
    """Validate amino acid sequence contains only standard residues."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    return all(aa in valid_aa for aa in sequence.upper())

def get_common_modifications() -> Dict[str, str]:
    """Return dictionary of common non-canonical amino acid modifications."""
    return MODIFICATION_MAP.copy()

def parse_modification_string(mod_string: str) -> List[Dict[str, Any]]:
    """
    Parse modification string in format: position:modification_name
    E.g., "3:phosphoserine,7:hydroxyproline"

    Args:
        mod_string: Comma-separated list of position:modification pairs

    Returns:
        List of modification dictionaries
    """
    if not mod_string:
        return []

    modifications = []
    mod_map = get_common_modifications()

    for mod in mod_string.split(','):
        if ':' not in mod:
            continue

        try:
            pos_str, mod_name = mod.strip().split(':')
            position = int(pos_str)

            # Look up CCD code
            if mod_name.lower() in mod_map:
                ccd = mod_map[mod_name.lower()]
            else:
                # Assume it's already a CCD code
                ccd = mod_name.upper()

            modifications.append({
                "position": position,
                "ccd": ccd
            })

        except ValueError:
            print(f"Warning: Invalid modification format: {mod}. Use position:modification_name")
            continue

    return modifications

def create_modified_peptide_config(
    sequence: str,
    modifications: List[Dict[str, Any]] = None,
    use_msa_server: bool = True,
    chain_id: str = "A"
) -> Dict[str, Any]:
    """Create configuration dictionary for modified cyclic peptide prediction."""
    config = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": chain_id,
                    "sequence": sequence,
                    "cyclic": True
                }
            }
        ]
    }

    # Add modifications if provided
    if modifications:
        config["sequences"][0]["protein"]["modifications"] = modifications

    # If not using MSA server, use single sequence mode
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
def run_predict_modified(
    input_sequence: str,
    modifications: Union[str, List[Dict[str, Any]]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Predict structure of cyclic peptide with non-canonical amino acids.

    Args:
        input_sequence: Base amino acid sequence (canonical residues)
        modifications: Either modification string or list of modification dicts
        output_dir: Directory to save prediction results (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result
            - output_dir: Path to output directory (if used)
            - metadata: Execution metadata

    Example:
        >>> result = run_predict_modified("QLEDSEVEAVAKG", "3:phosphoserine,7:hydroxyproline")
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

    # Parse modifications if provided as string
    if isinstance(modifications, str):
        modifications = parse_modification_string(modifications)
    elif modifications is None:
        modifications = []

    # Validate sequence if requested
    if config.get("validate_sequence", True):
        if not validate_amino_acid_sequence(sequence):
            return {
                "success": False,
                "error": "Invalid amino acid sequence. Please use standard single-letter codes.",
                "result": None,
                "output_dir": None,
                "metadata": {"sequence": sequence, "modifications": modifications, "config": config}
            }

    # Validate modification positions
    for mod in modifications:
        if mod["position"] < 1 or mod["position"] > len(sequence):
            return {
                "success": False,
                "error": f"Modification position {mod['position']} is out of range for sequence length {len(sequence)}",
                "result": None,
                "output_dir": None,
                "metadata": {"sequence": sequence, "modifications": modifications, "config": config}
            }

    # Setup output directory
    if output_dir is None:
        mod_suffix = f"_{len(modifications)}mods" if modifications else "_canonical"
        output_dir = f"./modified_cyclic_peptide_{len(sequence)}aa{mod_suffix}"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create YAML configuration
    peptide_config = create_modified_peptide_config(
        sequence,
        modifications,
        use_msa_server=config["use_msa_server"],
        chain_id=config["chain_id"]
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

        # Generate modification summary
        mod_summary = []
        for mod in modifications:
            pos = mod["position"]
            ccd = mod["ccd"]
            original_aa = sequence[pos-1] if pos <= len(sequence) else "?"
            mod_summary.append({
                "position": pos,
                "original_aa": original_aa,
                "ccd": ccd
            })

        return {
            "success": result["success"],
            "result": result,
            "output_dir": str(output_path),
            "output_files": output_files,
            "metadata": {
                "sequence": sequence,
                "sequence_length": len(sequence),
                "modifications": modifications,
                "modification_summary": mod_summary,
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
            "metadata": {"sequence": sequence, "modifications": modifications, "config": config}
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
        '--sequence', '-s',
        help='Base amino acid sequence of cyclic peptide (canonical residues)'
    )
    parser.add_argument(
        '--modifications', '-m',
        default="",
        help='Modifications in format "position:modification_name,position:modification_name"'
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
    parser.add_argument(
        '--list-modifications',
        action="store_true",
        help='List available modification types and exit'
    )

    args = parser.parse_args()

    # List available modifications if requested
    if args.list_modifications:
        print("Available non-canonical amino acid modifications:")
        print("=" * 50)
        mod_map = get_common_modifications()
        for name, ccd in sorted(mod_map.items()):
            print(f"  {name:<20} -> {ccd}")
        print("\nUsage: --modifications 'position:modification_name'")
        print("Example: --modifications '3:phosphoserine,7:hydroxyproline'")
        return 0

    # Require sequence unless listing modifications
    if not args.sequence:
        parser.error("--sequence is required unless --list-modifications is used")

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
    result = run_predict_modified(
        input_sequence=args.sequence,
        modifications=args.modifications,
        output_dir=args.output,
        config=config
    )

    if result["success"]:
        print(f"Success: Modified peptide prediction completed")
        print(f"Output directory: {result['output_dir']}")
        print(f"Sequence: {result['metadata']['sequence']}")
        if result['metadata']['modifications']:
            print(f"Modifications: {len(result['metadata']['modifications'])}")
            for mod_info in result['metadata']['modification_summary']:
                print(f"  Position {mod_info['position']}: {mod_info['original_aa']} -> {mod_info['ccd']}")
        else:
            print("Modifications: None (canonical cyclic peptide)")
        if result["output_files"]:
            print(f"Generated {len(result['output_files'])} files")
        return 0
    else:
        print(f"Error: {result['error']}")
        return 1

if __name__ == '__main__':
    exit(main())