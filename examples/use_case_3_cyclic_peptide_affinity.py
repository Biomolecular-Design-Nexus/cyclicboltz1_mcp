#!/usr/bin/env python
"""
Use Case 3: Cyclic Peptide-Target Binding Affinity Prediction

This script demonstrates how to predict binding affinities between cyclic
peptides and target proteins using Boltz-2. This is crucial for drug discovery
applications where cyclic peptides are designed to bind specific protein targets.

Input: Cyclic peptide sequence + target protein sequence
Output: Structure prediction + binding affinity predictions
"""

import argparse
import os
import subprocess
import tempfile
import yaml
import json
from pathlib import Path


def create_peptide_target_yaml(peptide_seq, target_seq, target_chain_id="A", peptide_chain_id="B", output_path="config.yaml", use_msa_server=True):
    """
    Create a YAML configuration for cyclic peptide-target complex prediction with affinity.

    Args:
        peptide_seq (str): Amino acid sequence of the cyclic peptide
        target_seq (str): Amino acid sequence of the target protein
        target_chain_id (str): Chain ID for target protein
        peptide_chain_id (str): Chain ID for cyclic peptide
        output_path (str): Path to save the YAML file
        use_msa_server (bool): Whether to use MSA server for sequence alignment
    """
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

    # If not using MSA server, use single sequence mode
    if not use_msa_server:
        config["sequences"][0]["protein"]["msa"] = "empty"
        config["sequences"][1]["protein"]["msa"] = "empty"

    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    return config


def run_boltz_affinity_prediction(yaml_path, output_dir, use_msa_server=True):
    """
    Run Boltz-2 prediction with affinity calculation.

    Args:
        yaml_path (str): Path to YAML configuration file
        output_dir (str): Directory to save predictions
        use_msa_server (bool): Whether to use MSA server
    """
    cmd = [
        "boltz", "predict", yaml_path,
        "--out_dir", output_dir,
        "--model", "boltz2",  # Affinity prediction requires Boltz-2
        "--accelerator", "cpu",  # Use CPU for compatibility
        "--diffusion_samples", "5",  # More samples for affinity prediction
        "--diffusion_samples_affinity", "5",  # Specific for affinity
        "--recycling_steps", "3"
    ]

    if use_msa_server:
        cmd.append("--use_msa_server")

    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Boltz affinity prediction completed successfully!")
        print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Boltz prediction: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def analyze_affinity_results(output_dir):
    """
    Parse and analyze the affinity prediction results.

    Args:
        output_dir (str): Directory containing prediction results
    """
    pred_dir = Path(output_dir) / "predictions"

    print("\n" + "="*60)
    print("BINDING AFFINITY ANALYSIS")
    print("="*60)

    # Find affinity files
    affinity_files = list(pred_dir.rglob("affinity_*.json"))

    if not affinity_files:
        print("No affinity files found.")
        return

    for affinity_file in affinity_files:
        print(f"\nAnalyzing: {affinity_file.name}")
        print("-" * 40)

        try:
            with open(affinity_file, 'r') as f:
                affinity_data = json.load(f)

            # Extract key affinity metrics
            affinity_value = affinity_data.get('affinity_pred_value', 'N/A')
            affinity_prob = affinity_data.get('affinity_probability_binary', 'N/A')

            print(f"Binding Affinity Value: {affinity_value}")
            if affinity_value != 'N/A':
                # Convert to IC50 and pIC50
                ic50_um = 10 ** affinity_value
                pic50 = (6 - affinity_value) * 1.364
                print(f"  → IC50: {ic50_um:.2e} μM")
                print(f"  → pIC50: {pic50:.2f} kcal/mol")

                # Interpret binding strength
                if affinity_value < -1:
                    strength = "Very Strong (nanomolar)"
                elif affinity_value < 0:
                    strength = "Strong (sub-micromolar)"
                elif affinity_value < 1:
                    strength = "Moderate (micromolar)"
                else:
                    strength = "Weak (>10 μM)"
                print(f"  → Binding Strength: {strength}")

            print(f"Binding Probability: {affinity_prob}")
            if affinity_prob != 'N/A':
                if affinity_prob > 0.8:
                    likelihood = "Very Likely"
                elif affinity_prob > 0.6:
                    likelihood = "Likely"
                elif affinity_prob > 0.4:
                    likelihood = "Moderate"
                else:
                    likelihood = "Unlikely"
                print(f"  → Binding Likelihood: {likelihood}")

            # Show ensemble predictions if available
            if 'affinity_pred_value1' in affinity_data:
                print(f"\nEnsemble Model 1:")
                print(f"  Affinity Value: {affinity_data.get('affinity_pred_value1', 'N/A')}")
                print(f"  Binding Prob: {affinity_data.get('affinity_probability_binary1', 'N/A')}")

            if 'affinity_pred_value2' in affinity_data:
                print(f"\nEnsemble Model 2:")
                print(f"  Affinity Value: {affinity_data.get('affinity_pred_value2', 'N/A')}")
                print(f"  Binding Prob: {affinity_data.get('affinity_probability_binary2', 'N/A')}")

        except Exception as e:
            print(f"Error reading affinity file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Predict cyclic peptide-target binding affinity using Boltz-2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Predict binding to a short target protein
    python use_case_3_cyclic_peptide_affinity.py \\
        --peptide "QLEDSEVEAVAKG" \\
        --target "MKLLVASILALAVCSGSAKETTVLTLSDQGKFSLCAGAKGATVDSSKLSLSLGSAQLVVHGEGTV"

    # Use default example sequences
    python use_case_3_cyclic_peptide_affinity.py

    # Specify custom output directory
    python use_case_3_cyclic_peptide_affinity.py --output_dir ./my_affinity_prediction

Notes:
    - Binding affinity prediction requires Boltz-2
    - Results include both IC50 values and binding probability
    - Lower affinity_pred_value indicates stronger binding
        """
    )

    parser.add_argument(
        "--peptide", "-p",
        default="QLEDSEVEAVAKG",
        help="Amino acid sequence of the cyclic peptide"
    )

    parser.add_argument(
        "--target", "-t",
        default="MKLLVASILALAVCSGSAKETTVLTLSDQGKFSLCAGAKGATVDSSKLSLSLGSAQLVVHGEGTV",
        help="Amino acid sequence of the target protein"
    )

    parser.add_argument(
        "--output_dir", "-o",
        default="./cyclic_affinity_prediction",
        help="Directory to save prediction results"
    )

    parser.add_argument(
        "--no_msa_server",
        action="store_true",
        help="Don't use MSA server (single sequence mode)"
    )

    args = parser.parse_args()

    # Validate sequences
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")

    if not all(aa in valid_aa for aa in args.peptide.upper()):
        print("Error: Invalid peptide sequence. Please use standard single-letter codes.")
        return 1

    if not all(aa in valid_aa for aa in args.target.upper()):
        print("Error: Invalid target sequence. Please use standard single-letter codes.")
        return 1

    # Check peptide size (Boltz has limits for affinity prediction)
    if len(args.peptide) > 50:  # Conservative limit
        print("Warning: Peptide sequence is quite long. Affinity prediction works best with smaller peptides.")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        print(f"Creating cyclic peptide-target binding configuration:")
        print(f"  Cyclic Peptide (Chain B): {args.peptide} ({len(args.peptide)} residues)")
        print(f"  Target Protein (Chain A): {args.target[:50]}{'...' if len(args.target) > 50 else ''} ({len(args.target)} residues)")
        print(f"  Output directory: {args.output_dir}")

        # Create YAML configuration
        config = create_peptide_target_yaml(
            args.peptide,
            args.target,
            output_path=yaml_path,
            use_msa_server=not args.no_msa_server
        )

        print("\nGenerated configuration:")
        print(yaml.dump(config, default_flow_style=False))

        # Run prediction
        success = run_boltz_affinity_prediction(
            yaml_path,
            args.output_dir,
            use_msa_server=not args.no_msa_server
        )

        if success:
            print(f"\nAffinity prediction completed! Results saved to: {args.output_dir}")

            # Analyze results
            analyze_affinity_results(args.output_dir)

            # List output files
            pred_dir = Path(args.output_dir) / "predictions"
            if pred_dir.exists():
                print(f"\n{'='*60}")
                print("GENERATED FILES")
                print("="*60)
                for file_path in pred_dir.rglob("*"):
                    if file_path.is_file():
                        print(f"  {file_path.relative_to(pred_dir)}")

            print(f"\n{'='*60}")
            print("INTERPRETATION GUIDE")
            print("="*60)
            print("Affinity Value (log10(IC50)):")
            print("  < -1: Very strong binding (nanomolar)")
            print("   -1 to 0: Strong binding (sub-micromolar)")
            print("    0 to 1: Moderate binding (micromolar)")
            print("      > 1: Weak binding (>10 μM)")
            print("\nBinding Probability:")
            print("  > 0.8: Very likely to bind")
            print("  0.6-0.8: Likely to bind")
            print("  0.4-0.6: Moderate binding likelihood")
            print("  < 0.4: Unlikely to bind")

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