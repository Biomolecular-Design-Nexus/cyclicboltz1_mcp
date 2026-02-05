"""
General utilities for cyclic peptide scripts.

These functions provide common utilities like chain ID generation,
sequence formatting, and other helper functions.
"""

from typing import List, Dict, Any, Union
from pathlib import Path


def generate_chain_ids(num_chains: int) -> List[str]:
    """
    Generate chain IDs (A, B, C, ...) for the given number of chains.

    Args:
        num_chains: Number of chain IDs to generate

    Returns:
        List of chain IDs

    Example:
        >>> generate_chain_ids(3)
        ['A', 'B', 'C']
        >>> generate_chain_ids(26)
        ['A', 'B', ..., 'Z']
    """
    if num_chains <= 0:
        return []

    if num_chains > 26:
        # For more than 26 chains, use A1, A2, etc.
        chains = []
        for i in range(num_chains):
            base = chr(ord('A') + (i % 26))
            suffix = "" if i < 26 else str((i // 26))
            chains.append(f"{base}{suffix}")
        return chains
    else:
        return [chr(ord('A') + i) for i in range(num_chains)]


def format_sequence_info(sequences: List[str], chain_ids: List[str] = None) -> str:
    """
    Format sequence information for display.

    Args:
        sequences: List of amino acid sequences
        chain_ids: List of chain IDs (generated if not provided)

    Returns:
        Formatted string describing the sequences

    Example:
        >>> seqs = ["ACDE", "FGHIK"]
        >>> format_sequence_info(seqs)
        'Chain A: ACDE (4 residues)\\nChain B: FGHIK (5 residues)'
    """
    if not sequences:
        return "No sequences provided"

    if chain_ids is None:
        chain_ids = generate_chain_ids(len(sequences))

    lines = []
    for seq, chain_id in zip(sequences, chain_ids):
        lines.append(f"Chain {chain_id}: {seq} ({len(seq)} residues)")

    return "\n".join(lines)


def create_output_directory_name(
    base_name: str,
    sequences: List[str] = None,
    chain_count: int = None,
    modifications: List[Dict] = None,
    suffix: str = ""
) -> str:
    """
    Create a descriptive output directory name based on input parameters.

    Args:
        base_name: Base name for the directory
        sequences: List of sequences (to calculate total length)
        chain_count: Number of chains (alternative to sequences)
        modifications: List of modifications
        suffix: Additional suffix

    Returns:
        Directory name

    Example:
        >>> create_output_directory_name("cyclic_peptide", ["ACDE", "FGHIK"])
        'cyclic_peptide_2chains_9aa'
        >>> create_output_directory_name("modified", ["ACDEFGH"], modifications=[{}, {}])
        'modified_1chains_7aa_2mods'
    """
    parts = [base_name]

    # Add chain count
    if sequences:
        chain_count = len(sequences)
        total_length = sum(len(seq) for seq in sequences)
        if chain_count == 1:
            parts.append(f"{total_length}aa")
        else:
            parts.append(f"{chain_count}chains_{total_length}aa")
    elif chain_count:
        if chain_count == 1:
            parts.append("single")
        else:
            parts.append(f"{chain_count}chains")

    # Add modification count
    if modifications:
        mod_count = len(modifications)
        if mod_count > 0:
            parts.append(f"{mod_count}mods")

    # Add suffix
    if suffix:
        parts.append(suffix)

    return "_".join(parts)


def truncate_sequence_for_display(sequence: str, max_length: int = 50) -> str:
    """
    Truncate sequence for display purposes.

    Args:
        sequence: Amino acid sequence
        max_length: Maximum length before truncation

    Returns:
        Truncated sequence with ellipsis if needed

    Example:
        >>> truncate_sequence_for_display("ACDEFGHIKLMNPQRST")
        'ACDEFGHIKLMNPQRST'
        >>> truncate_sequence_for_display("ACDEFGHIKLMNPQRST" * 5, 20)
        'ACDEFGHIKLMNPQRSTACDE...'
    """
    if len(sequence) <= max_length:
        return sequence
    else:
        return sequence[:max_length-3] + "..."


def calculate_sequence_stats(sequences: List[str]) -> Dict[str, Any]:
    """
    Calculate statistics for a list of sequences.

    Args:
        sequences: List of amino acid sequences

    Returns:
        Dictionary with sequence statistics

    Example:
        >>> stats = calculate_sequence_stats(["ACDE", "FGHIKLMN"])
        >>> print(stats["total_residues"])
        12
    """
    if not sequences:
        return {
            "sequence_count": 0,
            "total_residues": 0,
            "min_length": 0,
            "max_length": 0,
            "avg_length": 0.0
        }

    lengths = [len(seq) for seq in sequences]

    return {
        "sequence_count": len(sequences),
        "total_residues": sum(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "avg_length": sum(lengths) / len(lengths),
        "lengths": lengths
    }


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string

    Example:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1536)
        '1.5 KB'
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def summarize_output_files(file_paths: List[str]) -> Dict[str, Any]:
    """
    Summarize information about output files.

    Args:
        file_paths: List of file paths

    Returns:
        Dictionary with file summary information

    Example:
        >>> files = ["output/pred.cif", "output/conf.json"]
        >>> summary = summarize_output_files(files)
        >>> print(summary["total_count"])
    """
    if not file_paths:
        return {
            "total_count": 0,
            "total_size": 0,
            "by_extension": {},
            "largest_file": None,
            "largest_size": 0
        }

    by_extension = {}
    total_size = 0
    largest_file = None
    largest_size = 0

    for file_path in file_paths:
        path = Path(file_path)

        # Get file size
        try:
            size = path.stat().st_size
            total_size += size

            if size > largest_size:
                largest_size = size
                largest_file = file_path
        except (FileNotFoundError, OSError):
            size = 0

        # Count by extension
        ext = path.suffix.lower()
        if ext not in by_extension:
            by_extension[ext] = {"count": 0, "total_size": 0}
        by_extension[ext]["count"] += 1
        by_extension[ext]["total_size"] += size

    return {
        "total_count": len(file_paths),
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "by_extension": by_extension,
        "largest_file": largest_file,
        "largest_size": largest_size,
        "largest_size_formatted": format_file_size(largest_size) if largest_size > 0 else "0 B"
    }