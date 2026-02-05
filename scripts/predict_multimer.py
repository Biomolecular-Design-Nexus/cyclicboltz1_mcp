#!/usr/bin/env python3
"""
Script: predict_multimer.py
Description: Predict structures of multiple cyclic peptides and their interactions

Original Use Case: examples/use_case_2_cyclic_peptide_multimer.py
Dependencies Removed: None (was dependency-free)

Usage:
    python scripts/predict_multimer.py --sequences <seq1> <seq2> --output <output_dir>

Example:
    python scripts/predict_multimer.py --sequences "QLEDSEVEAVAKG" "MKLFWDESG" --output results/multimer
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
    "diffusion_samples": 3,
    "recycling_steps": 5,
    "use_msa_server": True,
    "validate_sequences": True,
    "auto_chain_ids": True
}

# ==============================================================================
# Utility Functions (inlined from use case)
# ==============================================================================
def validate_amino_acid_sequence(sequence: str) -> bool:
    """Validate amino acid sequence contains only standard residues."""
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    return all(aa in valid_aa for aa in sequence.upper())

def generate_chain_ids(num_chains: int) -> List[str]:
    """Generate chain IDs (A, B, C, ...) for the given number of chains."""
    return [chr(ord('A') + i) for i in range(num_chains)]

def create_cyclic_multimer_config(
    sequences: List[str],
    chain_ids: Optional[List[str]] = None,
    use_msa_server: bool = True
) -> Dict[str, Any]:
    """Create configuration dictionary for cyclic peptide multimer prediction."""
    if chain_ids is None:
        chain_ids = generate_chain_ids(len(sequences))

    if len(sequences) != len(chain_ids):
        raise ValueError("Number of sequences must match number of chain IDs")

    config = {
        "version": 1,
        "sequences": []
    }

    for sequence, chain_id in zip(sequences, chain_ids):
        chain_config = {
            "protein": {
                "id": chain_id,
                "sequence": sequence,
                "cyclic": True  # Each peptide in the multimer is cyclic
            }
        }

        if not use_msa_server:
            chain_config["protein"]["msa"] = "empty"

        config["sequences"].append(chain_config)

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
def run_predict_multimer(
    input_sequences: List[str],
    output_dir: Optional[Union[str, Path]] = None,
    chain_ids: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Predict structures of multiple cyclic peptides and their interactions.

    Args:
        input_sequences: List of amino acid sequences of cyclic peptides
        output_dir: Directory to save prediction results (optional)
        chain_ids: List of chain IDs (auto-generated if not provided)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result
            - output_dir: Path to output directory (if used)
            - metadata: Execution metadata

    Example:
        >>> result = run_predict_multimer(["QLEDSEVEAVAKG", "MKLFWDESG"], "results/multimer")
        >>> print(result['success'])
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_sequences or len(input_sequences) < 2:
        return {
            "success": False,
            "error": "At least 2 sequences required for multimer prediction",
            "result": None,
            "output_dir": None,
            "metadata": {"config": config}
        }

    # Clean sequences
    sequences = [seq.strip().upper() for seq in input_sequences]

    # Auto-generate chain IDs if not provided
    if chain_ids is None and config.get("auto_chain_ids", True):
        chain_ids = generate_chain_ids(len(sequences))

    if chain_ids and len(sequences) != len(chain_ids):
        return {
            "success": False,
            "error": "Number of sequences must match number of chain IDs",
            "result": None,
            "output_dir": None,
            "metadata": {"sequences": sequences, "chain_ids": chain_ids, "config": config}
        }

    # Check for duplicate chain IDs
    if chain_ids and len(set(chain_ids)) != len(chain_ids):
        return {
            "success": False,
            "error": "Chain IDs must be unique",
            "result": None,
            "output_dir": None,
            "metadata": {"sequences": sequences, "chain_ids": chain_ids, "config": config}
        }

    # Validate sequences if requested
    if config.get("validate_sequences", True):
        for i, sequence in enumerate(sequences):
            if not validate_amino_acid_sequence(sequence):
                return {
                    "success": False,
                    "error": f"Invalid amino acid sequence {i+1}. Please use standard single-letter codes.",
                    "result": None,
                    "output_dir": None,
                    "metadata": {"sequences": sequences, "chain_ids": chain_ids, "config": config}
                }

    # Setup output directory
    if output_dir is None:
        total_length = sum(len(seq) for seq in sequences)
        output_dir = f"./cyclic_multimer_prediction_{len(sequences)}chains_{total_length}aa"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create YAML configuration
    multimer_config = create_cyclic_multimer_config(
        sequences,
        chain_ids,
        use_msa_server=config["use_msa_server"]
    )

    # Use temporary file for YAML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        save_yaml_config(multimer_config, yaml_path)

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
                "sequences": sequences,
                "chain_ids": chain_ids,
                "sequence_lengths": [len(seq) for seq in sequences],
                "total_residues": sum(len(seq) for seq in sequences),
                "config": config,
                "yaml_config": multimer_config
            },
            "error": result.get("error") if not result["success"] else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "result": None,
            "output_dir": str(output_path) if output_dir else None,
            "metadata": {"sequences": sequences, "chain_ids": chain_ids, "config": config}
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
        '--sequences', '-s',
        nargs='+',
        required=True,
        help='Amino acid sequences of cyclic peptides (space-separated)'
    )
    parser.add_argument(
        '--chain-ids', '-c',
        nargs='+',
        help='Chain IDs for each sequence (auto-generated if not provided)'
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
    result = run_predict_multimer(
        input_sequences=args.sequences,
        output_dir=args.output,
        chain_ids=args.chain_ids,
        config=config
    )

    if result["success"]:
        print(f"Success: Multimer prediction completed")
        print(f"Output directory: {result['output_dir']}")
        print(f"Chains: {result['metadata']['chain_ids']}")
        print(f"Lengths: {result['metadata']['sequence_lengths']}")
        if result["output_files"]:
            print(f"Generated {len(result['output_files'])} files")
        return 0
    else:
        print(f"Error: {result['error']}")
        return 1

if __name__ == '__main__':
    exit(main())