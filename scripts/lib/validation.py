"""
Input validation utilities for cyclic peptide scripts.

These functions are extracted and simplified from the original use cases
to provide consistent validation across all scripts.
"""

from typing import List, Dict, Any


def validate_amino_acid_sequence(sequence: str) -> bool:
    """
    Validate amino acid sequence contains only standard residues.

    Args:
        sequence: Amino acid sequence to validate

    Returns:
        True if sequence contains only valid amino acids, False otherwise

    Example:
        >>> validate_amino_acid_sequence("ACDEFGH")
        True
        >>> validate_amino_acid_sequence("ACDEFGHX")
        False
    """
    if not sequence:
        return False

    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    return all(aa in valid_aa for aa in sequence.upper())


def validate_modification_positions(
    modifications: List[Dict[str, Any]],
    sequence_length: int
) -> List[str]:
    """
    Validate that modification positions are within sequence bounds.

    Args:
        modifications: List of modification dictionaries with 'position' key
        sequence_length: Length of the target sequence

    Returns:
        List of error messages (empty list if all valid)

    Example:
        >>> mods = [{"position": 1, "ccd": "SEP"}, {"position": 5, "ccd": "HYP"}]
        >>> validate_modification_positions(mods, 10)
        []
        >>> validate_modification_positions(mods, 3)
        ['Modification position 5 is out of range for sequence length 3']
    """
    errors = []

    for mod in modifications:
        pos = mod.get("position")
        if pos is None:
            errors.append("Modification missing 'position' field")
            continue

        if not isinstance(pos, int):
            errors.append(f"Modification position must be integer, got {type(pos)}")
            continue

        if pos < 1 or pos > sequence_length:
            errors.append(
                f"Modification position {pos} is out of range for sequence length {sequence_length}"
            )

    return errors


def validate_chain_ids(chain_ids: List[str]) -> List[str]:
    """
    Validate chain IDs are unique and valid.

    Args:
        chain_ids: List of chain identifiers

    Returns:
        List of error messages (empty list if all valid)

    Example:
        >>> validate_chain_ids(["A", "B", "C"])
        []
        >>> validate_chain_ids(["A", "B", "A"])
        ['Chain IDs must be unique: duplicate A found']
    """
    errors = []

    # Check for duplicates
    if len(set(chain_ids)) != len(chain_ids):
        duplicates = [cid for cid in set(chain_ids) if chain_ids.count(cid) > 1]
        errors.append(f"Chain IDs must be unique: duplicate {', '.join(duplicates)} found")

    # Check for invalid characters (should be single letter/digit)
    for cid in chain_ids:
        if not cid or len(cid) != 1 or not cid.isalnum():
            errors.append(f"Invalid chain ID '{cid}': must be single alphanumeric character")

    return errors


def validate_sequence_count(sequences: List[str], min_count: int = 1, max_count: int = 100) -> List[str]:
    """
    Validate number of sequences is within acceptable range.

    Args:
        sequences: List of amino acid sequences
        min_count: Minimum required sequences
        max_count: Maximum allowed sequences

    Returns:
        List of error messages (empty list if valid)
    """
    errors = []

    if len(sequences) < min_count:
        errors.append(f"At least {min_count} sequence(s) required, got {len(sequences)}")

    if len(sequences) > max_count:
        errors.append(f"Too many sequences: maximum {max_count} allowed, got {len(sequences)}")

    return errors