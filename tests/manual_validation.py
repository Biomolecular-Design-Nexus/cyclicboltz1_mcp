#!/usr/bin/env python3
"""Manual validation tests for MCP server tools."""

import sys
from pathlib import Path
import json
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import (
    get_server_info, validate_peptide_sequence,
    submit_structure_prediction, get_job_status,
    list_jobs, cancel_job, get_job_log
)

def test_server_info():
    """Test get_server_info function."""
    print("Testing get_server_info()...")
    try:
        # Access the underlying function, not the MCP tool wrapper
        info = get_server_info.__wrapped__()
        print("✅ get_server_info:", info.get("server_name"), info.get("version"))
        return True
    except Exception as e:
        print(f"❌ get_server_info failed: {e}")
        return False

def test_sequence_validation():
    """Test validate_peptide_sequence function."""
    print("Testing validate_peptide_sequence()...")
    try:
        # Test valid sequence
        result = validate_peptide_sequence.__wrapped__("GRGDSP")
        assert result["status"] == "success"
        assert result["valid"] == True
        print("✅ Valid sequence test passed")

        # Test invalid sequence
        result = validate_peptide_sequence.__wrapped__("GRGDXP")
        assert result["status"] == "success"
        assert result["valid"] == False
        assert "Invalid amino acids" in str(result["issues"])
        print("✅ Invalid sequence test passed")

        # Test empty sequence
        result = validate_peptide_sequence.__wrapped__("")
        assert result["valid"] == False
        assert "Empty sequence" in str(result["issues"])
        print("✅ Empty sequence test passed")

        return True
    except Exception as e:
        print(f"❌ validate_peptide_sequence failed: {e}")
        return False

def test_job_submission():
    """Test job submission and management."""
    print("Testing job submission workflow...")
    try:
        # Submit a job
        result = submit_structure_prediction.__wrapped__(
            sequence="GRGDSP",
            job_name="test_job"
        )
        print(f"Job submission result: {result}")

        if result["status"] != "submitted":
            print(f"❌ Job submission failed: {result}")
            return False

        job_id = result["job_id"]
        print(f"✅ Job submitted with ID: {job_id}")

        # Check job status
        time.sleep(1)  # Give it a moment
        status = get_job_status.__wrapped__(job_id)
        print(f"Job status: {status}")

        if status.get("job_id") != job_id:
            print(f"❌ Job status check failed")
            return False

        print(f"✅ Job status checked: {status.get('status')}")

        # List jobs
        jobs = list_jobs.__wrapped__()
        print(f"Jobs list: {jobs}")

        if not any(job.get("job_id") == job_id for job in jobs.get("jobs", [])):
            print(f"❌ Job not found in jobs list")
            return False

        print("✅ Job found in jobs list")

        # Try to get logs (may not exist yet)
        try:
            logs = get_job_log.__wrapped__(job_id, tail=10)
            print(f"Job logs: {logs.get('status')}")
        except Exception as e:
            print(f"⚠️ Log retrieval expected to fail for new job: {e}")

        # Cancel the job (since we don't want it running)
        cancel_result = cancel_job.__wrapped__(job_id)
        print(f"Cancel result: {cancel_result}")

        return True
    except Exception as e:
        print(f"❌ Job workflow failed: {e}")
        return False

def main():
    """Run manual validation tests."""
    print("=" * 50)
    print("Manual MCP Tool Validation Tests")
    print("=" * 50)

    tests = [
        ("Server Info", test_server_info),
        ("Sequence Validation", test_sequence_validation),
        ("Job Workflow", test_job_submission)
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\n[{passed + 1}/{len(tests)}] {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")

    print("\n" + "=" * 50)
    print(f"Manual Tests: {passed}/{len(tests)} passed")
    print("=" * 50)

    if passed == len(tests):
        print("🎉 All manual tests passed!")
        return True
    else:
        print("❌ Some manual tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)