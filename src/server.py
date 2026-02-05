"""MCP Server for Cyclic Peptide Tools

Provides both synchronous and asynchronous (submit) APIs for all tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List
import sys

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("cycpep-tools")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted cyclic peptide computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed cyclic peptide computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running cyclic peptide computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted cyclic peptide computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_structure_prediction(
    sequence: str,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a 3D structure prediction job for a cyclic peptide.

    This task typically takes more than 10 minutes. Use get_job_status() to monitor
    progress and get_job_result() to retrieve results when completed.

    Args:
        sequence: Amino acid sequence of the cyclic peptide (e.g., "QLEDSEVEAVAKG")
        output_dir: Optional output directory path (defaults to auto-generated)
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    script_path = str(SCRIPTS_DIR / "predict_structure.py")

    args = {"input": sequence}
    if output_dir:
        args["output"] = output_dir

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"structure_{sequence[:10]}"
    )

@mcp.tool()
def submit_multimer_prediction(
    sequences: List[str],
    output_dir: Optional[str] = None,
    chain_ids: Optional[List[str]] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a multimer structure prediction job for multiple cyclic peptides.

    Predicts structures and interactions of multiple cyclic peptides.
    This is a long-running task (typically 15+ minutes).

    Args:
        sequences: List of amino acid sequences (e.g., ["QLEDSEVEAVAKG", "MKLFWDESG"])
        output_dir: Optional output directory path
        chain_ids: Optional list of chain identifiers (auto-generated if None)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking
    """
    script_path = str(SCRIPTS_DIR / "predict_multimer.py")

    args = {"sequences": " ".join(f'"{seq}"' for seq in sequences)}
    if output_dir:
        args["output"] = output_dir
    if chain_ids:
        args["chain_ids"] = " ".join(chain_ids)

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"multimer_{len(sequences)}_peptides"
    )

@mcp.tool()
def submit_affinity_prediction(
    peptide_sequence: str,
    target_sequence: str,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a binding affinity prediction job between cyclic peptide and protein target.

    ⚠️  IMPORTANT NOTE: This tool has known limitations. Boltz affinity prediction
    currently only supports small molecule ligands, not peptide-peptide interactions.
    This may fail with "Chain B is not a ligand!" error.

    Args:
        peptide_sequence: Amino acid sequence of the cyclic peptide
        target_sequence: Amino acid sequence of the target protein
        output_dir: Optional output directory path
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking (may fail during execution)
    """
    script_path = str(SCRIPTS_DIR / "predict_affinity.py")

    args = {
        "peptide": peptide_sequence,
        "target": target_sequence
    }
    if output_dir:
        args["output"] = output_dir

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"affinity_{peptide_sequence[:8]}"
    )

@mcp.tool()
def submit_modified_peptide_prediction(
    sequence: str,
    modifications: Optional[str] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a structure prediction job for cyclic peptide with non-canonical amino acids.

    Predicts structure of cyclic peptides containing modified amino acids.

    Args:
        sequence: Base amino acid sequence of the cyclic peptide
        modifications: Modifications specification (e.g., "3:phosphoserine,7:hydroxyproline")
        output_dir: Optional output directory path
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking
    """
    script_path = str(SCRIPTS_DIR / "predict_modified.py")

    args = {"sequence": sequence}
    if modifications:
        args["modifications"] = modifications
    if output_dir:
        args["output"] = output_dir

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"modified_{sequence[:10]}"
    )

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def list_available_modifications() -> dict:
    """
    List all available non-canonical amino acid modifications.

    Returns:
        Dictionary with available modifications and their descriptions
    """
    try:
        # Import the function to list modifications
        script_path = str(SCRIPTS_DIR / "predict_modified.py")

        # Execute the script with --list-modifications flag
        import subprocess
        result = subprocess.run(
            ["python", script_path, "--list-modifications"],
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR.parent)
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "modifications": result.stdout.strip()
            }
        else:
            return {
                "status": "error",
                "error": f"Failed to list modifications: {result.stderr}"
            }
    except Exception as e:
        logger.error(f"Failed to list modifications: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def validate_peptide_sequence(sequence: str) -> dict:
    """
    Validate an amino acid sequence for cyclic peptide prediction.

    Checks if the sequence contains only standard amino acids and is suitable
    for structure prediction.

    Args:
        sequence: Amino acid sequence to validate

    Returns:
        Dictionary with validation results and any issues found
    """
    try:
        # Basic validation
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence = sequence.upper().strip()

        issues = []
        if not sequence:
            issues.append("Empty sequence")
        elif len(sequence) < 3:
            issues.append("Sequence too short (minimum 3 residues)")
        elif len(sequence) > 100:
            issues.append("Sequence very long (>100 residues, may be slow)")

        invalid_chars = set(sequence) - valid_aa
        if invalid_chars:
            issues.append(f"Invalid amino acids: {', '.join(sorted(invalid_chars))}")

        return {
            "status": "success",
            "valid": len(issues) == 0,
            "sequence": sequence,
            "length": len(sequence),
            "issues": issues
        }
    except Exception as e:
        logger.error(f"Sequence validation failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the CycPep MCP server.

    Returns:
        Dictionary with server information, available tools, and capabilities
    """
    return {
        "status": "success",
        "server_name": "cycpep-tools",
        "version": "1.0.0",
        "description": "MCP server for cyclic peptide computational tools using Boltz",
        "capabilities": {
            "structure_prediction": "3D structure prediction for cyclic peptides",
            "multimer_prediction": "Multi-peptide complex structure prediction",
            "affinity_prediction": "Peptide-target binding affinity (limited)",
            "modified_peptides": "Structure prediction with non-canonical amino acids"
        },
        "api_types": {
            "submit": "Long-running tasks with job tracking",
            "job_management": "Status, results, logs, cancellation"
        },
        "job_management": {
            "status_check": "get_job_status(job_id)",
            "get_results": "get_job_result(job_id)",
            "view_logs": "get_job_log(job_id)",
            "cancel": "cancel_job(job_id)",
            "list_all": "list_jobs(status)"
        },
        "supported_formats": ["amino acid sequences", "JSON output"],
        "limitations": [
            "Boltz dependency required for actual execution",
            "Affinity prediction limited to small molecule ligands",
            "GPU recommended for faster processing"
        ]
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()