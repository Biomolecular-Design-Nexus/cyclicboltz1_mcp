"""
Configuration management utilities for cyclic peptide scripts.

These functions handle loading, merging, and saving configuration files
in various formats (JSON, YAML).
"""

import json
import yaml
from pathlib import Path
from typing import Union, Dict, Any, Optional


def load_config_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from JSON or YAML file.

    Args:
        file_path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is unsupported or invalid

    Example:
        >>> config = load_config_file("configs/predict_structure_config.json")
        >>> print(config["model"]["name"])
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            if file_path.suffix.lower() == '.json':
                return json.load(f)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                # Try to auto-detect format
                content = f.read()
                f.seek(0)
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return yaml.safe_load(content)

    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise ValueError(f"Invalid configuration file format: {e}")


def save_yaml_config(config: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        file_path: Path to save the file

    Example:
        >>> config = {"version": 1, "sequences": [...]}
        >>> save_yaml_config(config, "temp_config.yaml")
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.

    Later configs override earlier ones. Nested dictionaries are merged recursively.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration dictionary

    Example:
        >>> base = {"model": {"name": "boltz1"}, "samples": 1}
        >>> override = {"model": {"device": "gpu"}, "samples": 3}
        >>> merged = merge_configs(base, override)
        >>> # Result: {"model": {"name": "boltz1", "device": "gpu"}, "samples": 3}
    """
    if not configs:
        return {}

    result = {}

    for config in configs:
        if not config:
            continue

        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value

    return result


def extract_nested_config(config: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Extract nested configuration value using dot notation.

    Args:
        config: Configuration dictionary
        *keys: Nested keys to traverse
        default: Default value if key not found

    Returns:
        Configuration value or default

    Example:
        >>> config = {"model": {"name": "boltz1", "device": "cpu"}}
        >>> extract_nested_config(config, "model", "name")
        'boltz1'
        >>> extract_nested_config(config, "model", "memory", default="auto")
        'auto'
    """
    current = config

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def flatten_config(config: Dict[str, Any], prefix: str = "", separator: str = ".") -> Dict[str, Any]:
    """
    Flatten nested configuration dictionary.

    Args:
        config: Configuration dictionary to flatten
        prefix: Prefix for keys
        separator: Separator between nested keys

    Returns:
        Flattened configuration dictionary

    Example:
        >>> config = {"model": {"name": "boltz1", "device": "cpu"}, "samples": 1}
        >>> flatten_config(config)
        {'model.name': 'boltz1', 'model.device': 'cpu', 'samples': 1}
    """
    flattened = {}

    for key, value in config.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            flattened.update(flatten_config(value, new_key, separator))
        else:
            flattened[new_key] = value

    return flattened


def create_default_config(script_type: str) -> Dict[str, Any]:
    """
    Create default configuration for a given script type.

    Args:
        script_type: Type of script ("structure", "multimer", "affinity", "modified")

    Returns:
        Default configuration dictionary

    Example:
        >>> config = create_default_config("structure")
        >>> print(config["model"]["name"])
        'boltz1'
    """
    base_config = {
        "model": {"name": "boltz1"},
        "processing": {
            "accelerator": "cpu",
            "use_msa_server": True
        },
        "validation": {
            "validate_sequence": True
        },
        "output": {
            "auto_output_dir": True
        }
    }

    specific_configs = {
        "structure": {
            "processing": {
                "diffusion_samples": 1,
                "recycling_steps": 3
            },
            "output": {"chain_id": "A"}
        },
        "multimer": {
            "processing": {
                "diffusion_samples": 3,
                "recycling_steps": 5
            },
            "multimer": {
                "auto_chain_ids": True,
                "min_chains": 2
            }
        },
        "affinity": {
            "model": {"name": "boltz2"},
            "processing": {
                "diffusion_samples": 5,
                "diffusion_samples_affinity": 5,
                "recycling_steps": 3
            },
            "affinity": {
                "target_chain_id": "A",
                "peptide_chain_id": "B"
            }
        },
        "modified": {
            "model": {"name": "boltz2"},
            "processing": {
                "diffusion_samples": 2,
                "recycling_steps": 5
            },
            "modifications": {"chain_id": "A"}
        }
    }

    if script_type in specific_configs:
        return merge_configs(base_config, specific_configs[script_type])
    else:
        return base_config