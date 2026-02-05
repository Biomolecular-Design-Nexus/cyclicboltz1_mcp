"""
Boltz prediction utilities for cyclic peptide scripts.

These functions handle running Boltz predictions via subprocess
and provide consistent command generation across all scripts.
"""

import subprocess
from pathlib import Path
from typing import Union, Dict, Any, List, Optional


def create_boltz_command(
    yaml_path: Union[str, Path],
    output_dir: Union[str, Path],
    config: Dict[str, Any]
) -> List[str]:
    """
    Create Boltz command line arguments.

    Args:
        yaml_path: Path to YAML configuration file
        output_dir: Output directory for predictions
        config: Configuration dictionary

    Returns:
        List of command line arguments

    Example:
        >>> config = {"model": {"name": "boltz1"}, "processing": {"accelerator": "cpu"}}
        >>> cmd = create_boltz_command("config.yaml", "output/", config)
        >>> print(cmd)
        ['boltz', 'predict', 'config.yaml', '--out_dir', 'output/', '--model', 'boltz1', '--accelerator', 'cpu']
    """
    cmd = [
        "boltz", "predict", str(yaml_path),
        "--out_dir", str(output_dir)
    ]

    # Model selection
    model = config.get("model", {}).get("name", "boltz1")
    cmd.extend(["--model", model])

    # Processing options
    processing = config.get("processing", {})

    if "accelerator" in processing:
        cmd.extend(["--accelerator", processing["accelerator"]])

    if "diffusion_samples" in processing:
        cmd.extend(["--diffusion_samples", str(processing["diffusion_samples"])])

    if "diffusion_samples_affinity" in processing:
        cmd.extend(["--diffusion_samples_affinity", str(processing["diffusion_samples_affinity"])])

    if "recycling_steps" in processing:
        cmd.extend(["--recycling_steps", str(processing["recycling_steps"])])

    if processing.get("use_msa_server", False):
        cmd.append("--use_msa_server")

    return cmd


def run_boltz_prediction(
    yaml_path: Union[str, Path],
    output_dir: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
    capture_output: bool = True,
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """
    Run Boltz prediction using subprocess.

    Args:
        yaml_path: Path to YAML configuration file
        output_dir: Directory to save predictions
        config: Configuration dictionary (uses defaults if None)
        capture_output: Whether to capture stdout/stderr
        timeout: Timeout in seconds (None for no timeout)

    Returns:
        Dictionary containing:
            - success: True if prediction succeeded
            - command: Command that was executed
            - stdout: Standard output (if captured)
            - stderr: Standard error (if captured)
            - error: Error message (if failed)

    Example:
        >>> result = run_boltz_prediction("config.yaml", "output/", {"model": {"name": "boltz1"}})
        >>> if result["success"]:
        ...     print("Prediction completed successfully")
        >>> else:
        ...     print(f"Prediction failed: {result['error']}")
    """
    # Default config if none provided
    if config is None:
        config = {
            "model": {"name": "boltz1"},
            "processing": {"accelerator": "cpu", "use_msa_server": True}
        }

    # Create command
    cmd = create_boltz_command(yaml_path, output_dir, config)

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=True,
            timeout=timeout
        )

        return {
            "success": True,
            "command": " ".join(cmd),
            "stdout": result.stdout if capture_output else None,
            "stderr": result.stderr if capture_output else None,
            "returncode": result.returncode
        }

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "command": " ".join(cmd),
            "stdout": e.stdout if capture_output else None,
            "stderr": e.stderr if capture_output else None,
            "returncode": e.returncode,
            "error": f"Boltz prediction failed with exit code {e.returncode}"
        }

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "command": " ".join(cmd),
            "stdout": e.stdout if capture_output else None,
            "stderr": e.stderr if capture_output else None,
            "error": f"Boltz prediction timed out after {timeout} seconds"
        }

    except FileNotFoundError:
        return {
            "success": False,
            "command": " ".join(cmd),
            "error": "Boltz command not found. Is Boltz installed and in PATH?"
        }

    except Exception as e:
        return {
            "success": False,
            "command": " ".join(cmd),
            "error": f"Unexpected error running Boltz: {e}"
        }


def check_boltz_availability() -> Dict[str, Any]:
    """
    Check if Boltz is available and get version info.

    Returns:
        Dictionary containing:
            - available: True if Boltz is found
            - version: Version string (if available)
            - error: Error message (if not available)

    Example:
        >>> status = check_boltz_availability()
        >>> if status["available"]:
        ...     print(f"Boltz {status['version']} is available")
        >>> else:
        ...     print(f"Boltz not found: {status['error']}")
    """
    try:
        result = subprocess.run(
            ["boltz", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

        return {
            "available": True,
            "version": result.stdout.strip(),
            "command_found": True
        }

    except subprocess.CalledProcessError:
        # Command found but failed (maybe no --version flag)
        return {
            "available": True,
            "version": "unknown",
            "command_found": True,
            "note": "Boltz command found but version could not be determined"
        }

    except FileNotFoundError:
        return {
            "available": False,
            "command_found": False,
            "error": "Boltz command not found in PATH"
        }

    except subprocess.TimeoutExpired:
        return {
            "available": False,
            "command_found": True,
            "error": "Boltz version check timed out"
        }

    except Exception as e:
        return {
            "available": False,
            "command_found": False,
            "error": f"Error checking Boltz availability: {e}"
        }


def parse_boltz_output_files(output_dir: Union[str, Path]) -> Dict[str, List[str]]:
    """
    Parse and categorize Boltz output files.

    Args:
        output_dir: Directory containing Boltz predictions

    Returns:
        Dictionary with categorized file paths:
            - structures: .cif structure files
            - confidence: confidence_*.json files
            - pae: pae_*.npz files
            - affinity: affinity_*.json files (if available)
            - all: all prediction files

    Example:
        >>> files = parse_boltz_output_files("results/predictions")
        >>> print(f"Found {len(files['structures'])} structure files")
    """
    output_path = Path(output_dir)
    pred_dir = output_path / "predictions"

    categorized = {
        "structures": [],
        "confidence": [],
        "pae": [],
        "affinity": [],
        "other": [],
        "all": []
    }

    if not pred_dir.exists():
        return categorized

    # Find all files in predictions directory
    for file_path in pred_dir.rglob("*"):
        if file_path.is_file():
            file_str = str(file_path)
            categorized["all"].append(file_str)

            # Categorize by type
            if file_path.suffix == ".cif":
                categorized["structures"].append(file_str)
            elif file_path.name.startswith("confidence_") and file_path.suffix == ".json":
                categorized["confidence"].append(file_str)
            elif file_path.name.startswith("pae_") and file_path.suffix == ".npz":
                categorized["pae"].append(file_str)
            elif file_path.name.startswith("affinity_") and file_path.suffix == ".json":
                categorized["affinity"].append(file_str)
            else:
                categorized["other"].append(file_str)

    return categorized