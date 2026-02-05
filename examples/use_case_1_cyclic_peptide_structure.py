#!/usr/bin/env python
"""
Use Case 1: Cyclic Peptide Structure Prediction

This script demonstrates how to predict the structure of a cyclic peptide
using Boltz. Cyclic peptides are formed by a covalent bond between the
N-terminal and C-terminal amino acids, creating a ring structure.

Input: Cyclic peptide sequence
Output: 3D structure prediction with confidence scores
"""

import argparse
import os
import subprocess
import tempfile
import yaml
from pathlib import Path


def create_cyclic_peptide_yaml(sequence, output_path, use_msa_server=True):
    """
    Create a YAML configuration for cyclic peptide structure prediction.

    Args:
        sequence (str): Amino acid sequence of the cyclic peptide
        output_path (str): Path to save the YAML file
        use_msa_server (bool): Whether to use MSA server for sequence alignment
    """
    config = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": "A",
                    "sequence": sequence,
                    "cyclic": True  # This is the key flag for cyclic peptides!
                }
            }
        ]
    }

    # If not using MSA server, we'd need to provide an MSA file
    if not use_msa_server:
        config["sequences"][0]["protein"]["msa"] = "empty"  # Single sequence mode

    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    return config


def run_boltz_prediction(yaml_path, output_dir, use_msa_server=True, model="boltz1"):
    """
    Run Boltz prediction on the cyclic peptide.

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
        "--diffusion_samples", "1",  # Single sample for demo
        "--recycling_steps", "3"
    ]

    if use_msa_server:
        cmd.append("--use_msa_server")

    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Boltz prediction completed successfully!")
        print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Boltz prediction: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Predict cyclic peptide structure using Boltz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Predict structure of a cyclic peptide using default sequence
    python use_case_1_cyclic_peptide_structure.py

    # Predict using custom sequence
    python use_case_1_cyclic_peptide_structure.py --sequence "QLEDSEVEAVAKG"

    # Use Boltz-2 model instead of Boltz-1
    python use_case_1_cyclic_peptide_structure.py --model boltz2
        """
    )

    parser.add_argument(
        "--sequence", "-s",
        default="QLEDSEVEAVAKG",  # Default from examples/cyclic_prot.yaml
        help="Amino acid sequence of the cyclic peptide"
    )

    parser.add_argument(
        "--output_dir", "-o",
        default="./cyclic_peptide_prediction",
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

    # Validate sequence (basic check for amino acid letters)
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    if not all(aa in valid_aa for aa in args.sequence.upper()):
        print("Error: Invalid amino acid sequence. Please use standard single-letter codes.")
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        print(f"Creating cyclic peptide configuration for sequence: {args.sequence}")
        print(f"Sequence length: {len(args.sequence)} residues")
        print(f"Output directory: {args.output_dir}")
        print(f"Model: {args.model}")

        # Create YAML configuration
        config = create_cyclic_peptide_yaml(
            args.sequence,
            yaml_path,
            use_msa_server=not args.no_msa_server
        )

        print("\nGenerated configuration:")
        print(yaml.dump(config, default_flow_style=False))

        # Run prediction
        success = run_boltz_prediction(
            yaml_path,
            args.output_dir,
            use_msa_server=not args.no_msa_server,
            model=args.model
        )

        if success:
            print(f"\nPrediction completed! Results saved to: {args.output_dir}")

            # List output files
            pred_dir = Path(args.output_dir) / "predictions"
            if pred_dir.exists():
                print("\nGenerated files:")
                for file_path in pred_dir.rglob("*"):
                    if file_path.is_file():
                        print(f"  {file_path}")

            print("\nKey outputs:")
            print("- *.cif: Predicted 3D structure")
            print("- confidence_*.json: Confidence scores (pLDDT, TM-score)")
            print("- pae_*.npz: Predicted Aligned Error matrix")

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