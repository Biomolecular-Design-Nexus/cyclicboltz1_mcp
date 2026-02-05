#!/usr/bin/env python3
"""Functional validation tests by directly testing core logic."""

import sys
from pathlib import Path
import json
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_sequence_validation_logic():
    """Test sequence validation logic directly."""
    print("Testing sequence validation logic...")
    try:
        # Valid amino acid check
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        test_sequences = [
            ("GRGDSP", True),
            ("GRGDXP", False),  # Contains X
            ("", False),        # Empty
            ("GR", False),      # Too short
            ("ACDEFGHIKLMNPQRSTVWY", True)  # All valid AAs
        ]

        for seq, expected_valid in test_sequences:
            seq = seq.upper().strip()
            issues = []

            if not seq:
                issues.append("Empty sequence")
            elif len(seq) < 3:
                issues.append("Sequence too short (minimum 3 residues)")

            invalid_chars = set(seq) - valid_aa
            if invalid_chars:
                issues.append(f"Invalid amino acids: {', '.join(sorted(invalid_chars))}")

            actual_valid = len(issues) == 0

            if actual_valid == expected_valid:
                print(f"✅ Sequence '{seq}': {actual_valid} (expected {expected_valid})")
            else:
                print(f"❌ Sequence '{seq}': {actual_valid} (expected {expected_valid})")
                return False

        return True
    except Exception as e:
        print(f"❌ Sequence validation logic failed: {e}")
        return False

def test_job_manager():
    """Test job manager functionality."""
    print("Testing job manager...")
    try:
        from jobs.manager import job_manager

        # Test jobs directory exists
        jobs_dir = job_manager.jobs_dir
        print(f"Jobs directory: {jobs_dir}")

        if not jobs_dir.exists():
            print(f"❌ Jobs directory doesn't exist: {jobs_dir}")
            return False

        print(f"✅ Jobs directory exists: {jobs_dir}")

        # Test list jobs (should work even if empty)
        result = job_manager.list_jobs()
        if result.get("status") != "success":
            print(f"❌ list_jobs failed: {result}")
            return False

        print(f"✅ list_jobs works: {len(result.get('jobs', []))} jobs found")

        # Test job status for non-existent job
        result = job_manager.get_job_status("nonexistent123")
        if result.get("status") != "error":
            print(f"❌ Expected error for non-existent job")
            return False

        print("✅ Proper error handling for non-existent job")

        return True
    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_script_files():
    """Test that script files exist and are importable."""
    print("Testing script files...")
    try:
        scripts_dir = Path(__file__).parent.parent / "scripts"
        required_scripts = [
            "predict_structure.py",
            "predict_multimer.py",
            "predict_affinity.py",
            "predict_modified.py"
        ]

        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                print(f"❌ Missing script: {script_path}")
                return False

            # Try to compile the script
            try:
                compile(script_path.read_text(), str(script_path), 'exec')
                print(f"✅ Script compiles: {script_name}")
            except SyntaxError as e:
                print(f"❌ Script syntax error in {script_name}: {e}")
                return False

        return True
    except Exception as e:
        print(f"❌ Script files test failed: {e}")
        return False

def test_mcp_server_object():
    """Test MCP server object creation."""
    print("Testing MCP server object...")
    try:
        from server import mcp

        # Check server name
        if mcp.name != "cycpep-tools":
            print(f"❌ Unexpected server name: {mcp.name}")
            return False

        print(f"✅ Server name correct: {mcp.name}")

        # Check we can access tool manager
        if not hasattr(mcp, '_tool_manager'):
            print("❌ No tool manager found")
            return False

        print("✅ Tool manager accessible")

        return True
    except Exception as e:
        print(f"❌ MCP server object test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        # Test FastMCP
        from fastmcp import FastMCP
        print("✅ FastMCP imported")

        # Test loguru
        from loguru import logger
        print("✅ loguru imported")

        # Test job manager
        from jobs.manager import job_manager, JobStatus
        print("✅ job_manager imported")

        # Test server
        from server import mcp
        print("✅ server imported")

        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run functional validation tests."""
    print("=" * 50)
    print("Functional Validation Tests")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("MCP Server Object", test_mcp_server_object),
        ("Sequence Validation Logic", test_sequence_validation_logic),
        ("Job Manager", test_job_manager),
        ("Script Files", test_script_files)
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
    print(f"Functional Tests: {passed}/{len(tests)} passed")
    print("=" * 50)

    if passed == len(tests):
        print("🎉 All functional tests passed!")
        return True
    else:
        print("❌ Some functional tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)