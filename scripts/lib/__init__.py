"""
Shared library for cyclic peptide MCP scripts.

This library contains common utilities extracted from the original use cases
to minimize code duplication and provide consistent functionality across scripts.
"""

from .validation import validate_amino_acid_sequence, validate_modification_positions
from .config import load_config_file, merge_configs, save_yaml_config
from .boltz import run_boltz_prediction, create_boltz_command
from .utils import generate_chain_ids, format_sequence_info

__version__ = "1.0.0"
__all__ = [
    "validate_amino_acid_sequence",
    "validate_modification_positions",
    "load_config_file",
    "merge_configs",
    "save_yaml_config",
    "run_boltz_prediction",
    "create_boltz_command",
    "generate_chain_ids",
    "format_sequence_info"
]