#!/usr/bin/env python
"""
Use Case 4: Non-canonical Amino Acid Support in Cyclic Peptides

This script demonstrates how to predict structures of cyclic peptides containing
non-canonical amino acids using Boltz. Non-canonical amino acids include
modified residues, D-amino acids, and other chemical modifications that enhance
peptide stability and binding properties.

Input: Cyclic peptide sequence with modifications
Output: 3D structure prediction accounting for modifications
"""

import argparse
import os
import subprocess
import tempfile
import yaml
from pathlib import Path


def create_modified_peptide_yaml(sequence, modifications, output_path, use_msa_server=True):
    """
    Create a YAML configuration for cyclic peptide with non-canonical amino acids.

    Args:
        sequence (str): Base amino acid sequence (canonical)
        modifications (list): List of dictionaries with position and CCD code
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

    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    return config


def get_common_modifications():
    """
    Return dictionary of common non-canonical amino acid modifications.
    """
    return {
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


def parse_modification_string(mod_string):
    """
    Parse modification string in format: position:modification_name
    E.g., "3:phosphoserine,7:hydroxyproline"

    Args:
        mod_string (str): Comma-separated list of position:modification pairs

    Returns:
        list: List of modification dictionaries
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


def run_boltz_prediction(yaml_path, output_dir, use_msa_server=True, model="boltz2"):
    """
    Run Boltz prediction on the modified cyclic peptide.

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
        "--diffusion_samples", "2",  # Multiple samples for modified peptides
        "--recycling_steps", "5"    # More recycling for complex modifications
    ]

    if use_msa_server:
        cmd.append("--use_msa_server")

    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Boltz prediction with modifications completed successfully!")
        print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Boltz prediction: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Predict cyclic peptide structure with non-canonical amino acids using Boltz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic cyclic peptide with phosphoserine at position 3
    python use_case_4_noncanonical_amino_acids.py \\
        --sequence "QLEDSEVEAVAKG" \\
        --modifications "3:phosphoserine"

    # Multiple modifications
    python use_case_4_noncanonical_amino_acids.py \\
        --sequence "QLEDSEVEAVAKG" \\
        --modifications "3:phosphoserine,7:hydroxyproline"

    # Using CCD codes directly
    python use_case_4_noncanonical_amino_acids.py \\
        --sequence "QLEDSEVEAVAKG" \\
        --modifications "3:SEP,7:HYP"

Available modifications:
    phosphoserine, phosphothreonine, phosphotyrosine, hydroxyproline,
    pyroglutamate, citrulline, ornithine, norleucine, selenocysteine,
    methylated_lysine, acetylated_lysine, and more...
        """
    )

    parser.add_argument(
        "--sequence", "-s",
        default="QLEDSEVEAVAKG",
        help="Base amino acid sequence of the cyclic peptide (canonical residues)"
    )

    parser.add_argument(
        "--modifications", "-m",
        default="",
        help="Modifications in format 'position:modification_name,position:modification_name'"
    )

    parser.add_argument(
        "--output_dir", "-o",
        default="./modified_cyclic_peptide",
        help="Directory to save prediction results"
    )

    parser.add_argument(
        "--model",
        choices=["boltz1", "boltz2"],
        default="boltz2",
        help="Boltz model to use for prediction (boltz2 recommended for modifications)"
    )

    parser.add_argument(
        "--no_msa_server",
        action="store_true",
        help="Don't use MSA server (single sequence mode)"
    )

    parser.add_argument(
        "--list_modifications",
        action="store_true",
        help="List available modification types and exit"
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

    # Validate sequence
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    if not all(aa in valid_aa for aa in args.sequence.upper()):
        print("Error: Invalid amino acid sequence. Please use standard single-letter codes.")
        return 1

    # Parse modifications
    modifications = parse_modification_string(args.modifications)

    # Validate modification positions
    for mod in modifications:
        if mod["position"] < 1 or mod["position"] > len(args.sequence):
            print(f"Error: Modification position {mod['position']} is out of range for sequence length {len(args.sequence)}")
            return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml_path = tmp_file.name

    try:
        print(f"Creating modified cyclic peptide configuration:")
        print(f"  Base sequence: {args.sequence} ({len(args.sequence)} residues)")
        if modifications:
            print(f"  Modifications:")
            for mod in modifications:
                pos = mod["position"]
                ccd = mod["ccd"]
                original_aa = args.sequence[pos-1] if pos <= len(args.sequence) else "?"
                print(f"    Position {pos}: {original_aa} -> {ccd}")
        else:
            print("  No modifications (canonical cyclic peptide)")
        print(f"  Output directory: {args.output_dir}")
        print(f"  Model: {args.model}")

        # Create YAML configuration
        config = create_modified_peptide_yaml(
            args.sequence,
            modifications,
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
            print(f"\nModified peptide prediction completed! Results saved to: {args.output_dir}")

            # List output files
            pred_dir = Path(args.output_dir) / "predictions"
            if pred_dir.exists():
                print("\nGenerated files:")
                for file_path in pred_dir.rglob("*"):
                    if file_path.is_file():
                        print(f"  {file_path}")

            print("\nKey outputs:")
            print("- *.cif: Predicted 3D structure with modifications")
            print("- confidence_*.json: Confidence scores")
            print("- pae_*.npz: Predicted Aligned Error matrix")

            if modifications:
                print("\nNotes on modifications:")
                print("- Modified residues should appear in the structure")
                print("- Check confidence scores near modification sites")
                print("- Some modifications may affect local structure stability")

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