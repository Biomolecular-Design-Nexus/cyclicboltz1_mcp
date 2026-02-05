#!/usr/bin/env python
"""
Use Case 2: Cyclic Peptide Multimer Prediction

This script demonstrates how to predict structures of multiple cyclic peptides
(multimers) and their potential interactions using Boltz. This is useful for
studying cyclic peptide assemblies, dimers, or higher-order complexes.

Input: Multiple cyclic peptide sequences
Output: 3D structure predictions showing peptide-peptide interactions
"""

import argparse
import os
import subprocess
import tempfile
import yaml
from pathlib import Path


def create_cyclic_multimer_yaml(sequences, chain_ids, output_path, use_msa_server=True):
    """
    Create a YAML configuration for cyclic peptide multimer prediction.

    Args:
        sequences (list): List of amino acid sequences
        chain_ids (list): List of chain IDs for each sequence
        output_path (str): Path to save the YAML file
        use_msa_server (bool): Whether to use MSA server for sequence alignment
    """
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

        # If not using MSA server, use single sequence mode
        if not use_msa_server:
            chain_config["protein"]["msa"] = "empty"

        config["sequences"].append(chain_config)

    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    return config


def run_boltz_multimer_prediction(yaml_path, output_dir, use_msa_server=True, model="boltz1"):
    """
    Run Boltz prediction on the cyclic peptide multimer.

    Args:
        yaml_path (str): Path to YAML configuration file
        output_dir (str): Directory to save predictions
        use_msa_server (bool): Whether to use MSA server
        model (str): Model to use (boltz1 or boltz2)
    """
    cmd = [
        "boltz", "predict", yaml_path,
        "--out_dir", output_dir,
        "--model", model,
        "--accelerator", "cpu",  # Use CPU for compatibility
        "--diffusion_samples", "3",  # Multiple samples for multimer diversity
        "--recycling_steps", "5"    # More recycling steps for complex interactions
    ]

    if use_msa_server:
        cmd.append("--use_msa_server")

    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Boltz multimer prediction completed successfully!")
        print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Boltz prediction: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Predict cyclic peptide multimer structures using Boltz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Predict dimer of identical cyclic peptides
    python use_case_2_cyclic_peptide_multimer.py

    # Predict heterodimer of different cyclic peptides
    python use_case_2_cyclic_peptide_multimer.py \\
        --sequences "QLEDSEVEAVAKG" "MKLFWDESG" \\
        --chain_ids "A" "B"

    # Predict trimer with custom sequences
    python use_case_2_cyclic_peptide_multimer.py \\
        --sequences "QLEDSEVEAVAKG" "QLEDSEVEAVAKG" "MKLFWDESG" \\
        --chain_ids "A" "B" "C"
        """
    )

    parser.add_argument(
        "--sequences", "-s",
        nargs="+",
        default=["QLEDSEVEAVAKG", "QLEDSEVEAVAKG"],  # Default dimer
        help="Amino acid sequences of the cyclic peptides"
    )

    parser.add_argument(
        "--chain_ids", "-c",
        nargs="+",
        default=["A", "B"],
        help="Chain IDs for each peptide sequence"
    )

    parser.add_argument(
        "--output_dir", "-o",
        default="./cyclic_multimer_prediction",
        help="Directory to save prediction results"
    )

    parser.add_argument(
        "--model", "-m",
        choices=["boltz1", "boltz2"],
        default="boltz1",
        help="Boltz model to use for prediction"
    )

    parser.add_argument(
        "--no_msa_server",
        action="store_true",
        help="Don't use MSA server (single sequence mode)"
    )

    args = parser.parse_args()

    # Validate inputs
    if len(args.sequences) != len(args.chain_ids):
        print("Error: Number of sequences must match number of chain IDs")
        return 1

    if len(args.sequences) < 2:
        print("Error: At least 2 sequences are required for multimer prediction")
        return 1

    # Validate sequences
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    for i, sequence in enumerate(args.sequences):
        if not all(aa in valid_aa for aa in sequence.upper()):
            print(f"Error: Invalid amino acid sequence {i+1}. Please use standard single-letter codes.")
            return 1

    # Check for duplicate chain IDs
    if len(set(args.chain_ids)) != len(args.chain_ids):
        print("Error: Chain IDs must be unique")
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        print(f"Creating cyclic peptide multimer configuration:")
        for i, (seq, chain_id) in enumerate(zip(args.sequences, args.chain_ids)):
            print(f"  Chain {chain_id}: {seq} ({len(seq)} residues)")
        print(f"Output directory: {args.output_dir}")
        print(f"Model: {args.model}")

        # Create YAML configuration
        config = create_cyclic_multimer_yaml(
            args.sequences,
            args.chain_ids,
            yaml_path,
            use_msa_server=not args.no_msa_server
        )

        print("\nGenerated configuration:")
        print(yaml.dump(config, default_flow_style=False))

        # Run prediction
        success = run_boltz_multimer_prediction(
            yaml_path,
            args.output_dir,
            use_msa_server=not args.no_msa_server,
            model=args.model
        )

        if success:
            print(f"\nMultimer prediction completed! Results saved to: {args.output_dir}")

            # List output files
            pred_dir = Path(args.output_dir) / "predictions"
            if pred_dir.exists():
                print("\nGenerated files:")
                for file_path in pred_dir.rglob("*"):
                    if file_path.is_file():
                        print(f"  {file_path}")

            print("\nKey outputs:")
            print("- *.cif: Predicted 3D structure of the multimer")
            print("- confidence_*.json: Confidence scores including interface metrics")
            print("- pae_*.npz: Predicted Aligned Error matrix")
            print("\nInterface analysis:")
            print("- Look for 'pair_chains_iptm' in confidence files for interface quality")
            print("- 'protein_iptm' indicates protein-protein interface confidence")

            return 0
        else:
            print("Prediction failed. Please check the error messages above.")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

    finally:
        # Clean up temporary file
        if os.path.exists(yaml_path):
            os.unlink(yaml_path)


if __name__ == "__main__":
    import sys
    sys.exit(main())