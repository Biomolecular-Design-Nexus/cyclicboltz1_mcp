#!/usr/bin/env python3
"""Automated integration test runner for Cyclic Peptide MCP server."""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class MCPTestRunner:
    """Test runner for MCP server validation."""

    def __init__(self, server_path: str = "src/server.py"):
        self.server_path = Path(server_path)
        self.project_root = self.server_path.parent.parent
        self.results = {
            "test_date": datetime.now().isoformat(),
            "server_path": str(self.server_path),
            "project_root": str(self.project_root),
            "tests": {},
            "issues": [],
            "summary": {}
        }

    def run_command(self, cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run a command and capture output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def test_server_startup(self) -> bool:
        """Test that server imports and starts without errors."""
        print("Testing server startup...")

        # Test import
        result = self.run_command([
            "python", "-c",
            "from src.server import mcp; print('Server imports OK')"
        ])

        self.results["tests"]["server_import"] = {
            "status": "passed" if result["success"] else "failed",
            "output": result["stdout"],
            "error": result["stderr"],
            "test_type": "import"
        }

        if not result["success"]:
            self.results["issues"].append({
                "test": "server_import",
                "severity": "critical",
                "description": "Server cannot be imported",
                "error": result["stderr"]
            })
            return False

        # Test job manager import
        result = self.run_command([
            "python", "-c",
            "from src.jobs.manager import job_manager; print('Job manager OK')"
        ])

        self.results["tests"]["job_manager_import"] = {
            "status": "passed" if result["success"] else "failed",
            "output": result["stdout"],
            "error": result["stderr"],
            "test_type": "import"
        }

        return result["success"]

    def test_dependencies(self) -> bool:
        """Test that required dependencies are available."""
        print("Testing dependencies...")

        dependencies = {
            "fastmcp": "from fastmcp import FastMCP; print('FastMCP OK')",
            "loguru": "from loguru import logger; print('Loguru OK')",
            "pathlib": "from pathlib import Path; print('Pathlib OK')"
        }

        all_ok = True
        for dep_name, test_code in dependencies.items():
            result = self.run_command(["python", "-c", test_code])

            self.results["tests"][f"dependency_{dep_name}"] = {
                "status": "passed" if result["success"] else "failed",
                "output": result["stdout"],
                "error": result["stderr"],
                "test_type": "dependency"
            }

            if not result["success"]:
                all_ok = False
                self.results["issues"].append({
                    "test": f"dependency_{dep_name}",
                    "severity": "high",
                    "description": f"Missing dependency: {dep_name}",
                    "error": result["stderr"]
                })

        return all_ok

    def test_script_files(self) -> bool:
        """Test that required script files exist."""
        print("Testing script files...")

        scripts_dir = self.project_root / "scripts"
        required_scripts = [
            "predict_structure.py",
            "predict_multimer.py",
            "predict_affinity.py",
            "predict_modified.py"
        ]

        all_exist = True
        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            exists = script_path.exists()

            self.results["tests"][f"script_{script_name}"] = {
                "status": "passed" if exists else "failed",
                "path": str(script_path),
                "exists": exists,
                "test_type": "file_existence"
            }

            if not exists:
                all_exist = False
                self.results["issues"].append({
                    "test": f"script_{script_name}",
                    "severity": "high",
                    "description": f"Missing required script: {script_name}",
                    "path": str(script_path)
                })

        return all_exist

    def test_claude_mcp_registration(self) -> bool:
        """Test Claude MCP server registration."""
        print("Testing Claude MCP registration...")

        # Check if server is registered
        result = self.run_command(["claude", "mcp", "list"])

        self.results["tests"]["mcp_registration"] = {
            "status": "passed" if result["success"] and "cycpep-tools" in result["stdout"] else "failed",
            "output": result["stdout"],
            "error": result["stderr"],
            "test_type": "mcp_registration"
        }

        if result["success"] and "cycpep-tools" in result["stdout"]:
            # Check connection status
            if "✓ Connected" in result["stdout"]:
                self.results["tests"]["mcp_connection"] = {
                    "status": "passed",
                    "output": "Server shows as connected",
                    "test_type": "mcp_connection"
                }
                return True
            else:
                self.results["tests"]["mcp_connection"] = {
                    "status": "failed",
                    "output": result["stdout"],
                    "error": "Server not showing as connected",
                    "test_type": "mcp_connection"
                }
                self.results["issues"].append({
                    "test": "mcp_connection",
                    "severity": "high",
                    "description": "MCP server registered but not connected",
                    "output": result["stdout"]
                })
                return False
        else:
            self.results["issues"].append({
                "test": "mcp_registration",
                "severity": "critical",
                "description": "cycpep-tools not found in MCP server list",
                "error": result["stderr"],
                "output": result["stdout"]
            })
            return False

    def test_job_directory(self) -> bool:
        """Test job directory setup."""
        print("Testing job directory setup...")

        jobs_dir = self.project_root / "jobs"

        # Test directory creation
        result = self.run_command([
            "python", "-c",
            f"from pathlib import Path; p = Path('{jobs_dir}'); p.mkdir(exist_ok=True); print(f'Jobs dir: {{p.exists()}}')"
        ])

        self.results["tests"]["job_directory"] = {
            "status": "passed" if result["success"] else "failed",
            "output": result["stdout"],
            "error": result["stderr"],
            "path": str(jobs_dir),
            "test_type": "directory"
        }

        return result["success"]

    def test_server_dev_mode(self) -> bool:
        """Test server can start in development mode."""
        print("Testing server development mode...")

        # Start server in dev mode with timeout
        result = self.run_command([
            "timeout", "10", "fastmcp", "dev", str(self.server_path)
        ], timeout=15)

        # We expect this to timeout (that means server started)
        # or show help/startup messages
        startup_ok = (
            result["returncode"] in [0, 124, -15] or  # timeout codes
            "FastMCP" in result["stdout"] or
            "cycpep-tools" in result["stdout"]
        )

        self.results["tests"]["server_dev_mode"] = {
            "status": "passed" if startup_ok else "failed",
            "output": result["stdout"][:500],  # Limit output size
            "error": result["stderr"][:500] if result["stderr"] else "",
            "returncode": result["returncode"],
            "test_type": "server_startup"
        }

        if not startup_ok:
            self.results["issues"].append({
                "test": "server_dev_mode",
                "severity": "high",
                "description": "Server failed to start in dev mode",
                "error": result["stderr"],
                "output": result["stdout"]
            })

        return startup_ok

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("=" * 60)
        print("Running MCP Server Integration Tests")
        print("=" * 60)

        test_functions = [
            ("Dependencies", self.test_dependencies),
            ("Script Files", self.test_script_files),
            ("Server Import", self.test_server_startup),
            ("Job Directory", self.test_job_directory),
            ("Claude MCP Registration", self.test_claude_mcp_registration),
            ("Server Dev Mode", self.test_server_dev_mode)
        ]

        passed = 0
        total = len(test_functions)

        for test_name, test_func in test_functions:
            print(f"\n[{passed + 1}/{total}] {test_name}...")
            try:
                success = test_func()
                if success:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                self.results["issues"].append({
                    "test": test_name.lower().replace(" ", "_"),
                    "severity": "critical",
                    "description": f"Test function crashed: {e}",
                    "error": str(e)
                })

        # Generate summary
        self.results["summary"] = {
            "total_tests": len(self.results["tests"]),
            "passed": sum(1 for t in self.results["tests"].values() if t.get("status") == "passed"),
            "failed": sum(1 for t in self.results["tests"].values() if t.get("status") == "failed"),
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
            "critical_issues": len([i for i in self.results["issues"] if i.get("severity") == "critical"]),
            "high_issues": len([i for i in self.results["issues"] if i.get("severity") == "high"]),
            "overall_status": "PASSED" if passed == total else "FAILED"
        }

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['summary']['total_tests']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Pass Rate: {self.results['summary']['pass_rate']}")
        print(f"Overall: {self.results['summary']['overall_status']}")

        if self.results["issues"]:
            print(f"\nIssues Found: {len(self.results['issues'])}")
            for issue in self.results["issues"]:
                print(f"  - [{issue['severity'].upper()}] {issue['test']}: {issue['description']}")
        else:
            print("\n🎉 No issues found!")

        return self.results

    def save_report(self, output_file: str = "reports/step7_integration_tests.json"):
        """Save test results to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nTest report saved to: {output_path}")

    def generate_markdown_report(self, output_file: str = "reports/step7_integration.md"):
        """Generate markdown report."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = f"""# Step 7: Integration Test Results

## Test Information
- **Test Date**: {self.results['test_date']}
- **Server Path**: `{self.results['server_path']}`
- **Project Root**: `{self.results['project_root']}`

## Summary
- **Total Tests**: {self.results['summary']['total_tests']}
- **Passed**: {self.results['summary']['passed']}
- **Failed**: {self.results['summary']['failed']}
- **Pass Rate**: {self.results['summary']['pass_rate']}
- **Overall Status**: {self.results['summary']['overall_status']}

## Test Results

| Test | Status | Type | Notes |
|------|--------|------|-------|
"""

        for test_name, test_data in self.results["tests"].items():
            status_icon = "✅" if test_data["status"] == "passed" else "❌"
            test_type = test_data.get("test_type", "unknown")
            notes = test_data.get("error", "")[:50] + "..." if test_data.get("error") else "OK"
            report += f"| {test_name} | {status_icon} {test_data['status']} | {test_type} | {notes} |\n"

        if self.results["issues"]:
            report += f"\n## Issues Found ({len(self.results['issues'])})\n\n"
            for i, issue in enumerate(self.results["issues"], 1):
                report += f"### Issue #{i}: {issue['test']}\n"
                report += f"- **Severity**: {issue['severity'].upper()}\n"
                report += f"- **Description**: {issue['description']}\n"
                if issue.get('error'):
                    report += f"- **Error**: `{issue['error']}`\n"
                if issue.get('output'):
                    report += f"- **Output**: `{issue['output'][:200]}`\n"
                report += "\n"
        else:
            report += "\n## 🎉 No Issues Found\n\nAll tests passed successfully!\n"

        report += f"""
## Next Steps

### If Tests Passed ✅
1. Proceed with manual testing using prompts in `tests/test_prompts.md`
2. Test real-world scenarios with Claude Code
3. Document any discovered limitations

### If Tests Failed ❌
1. Fix critical issues first (server import, dependencies)
2. Address high-priority issues (script files, MCP registration)
3. Re-run tests to verify fixes
4. Check installation instructions in README.md

## Test Environment
- Python: {sys.version.split()[0]}
- Working Directory: {Path.cwd()}
- Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(output_path, 'w') as f:
            f.write(report)

        print(f"Markdown report saved to: {output_path}")

def main():
    """Run the test suite."""
    runner = MCPTestRunner()

    try:
        results = runner.run_all_tests()
        runner.save_report()
        runner.generate_markdown_report()

        # Exit with error code if tests failed
        if results["summary"]["overall_status"] != "PASSED":
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest runner crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()