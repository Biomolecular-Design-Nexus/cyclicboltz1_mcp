# Installation & Validation Checklist for Cyclic Peptide MCP Server

Use this checklist to verify successful installation and integration of the Cyclic Peptide MCP server with Claude Code.

## Pre-Installation Requirements

### Environment Setup
- [ ] Python 3.10+ installed
- [ ] Conda or Mamba package manager available
- [ ] Claude Code CLI installed and working
- [ ] Git repository cloned to local machine

### Dependency Check
```bash
# Check Python version
python --version  # Should be 3.10+

# Check Claude Code CLI
claude --help  # Should show help menu

# Check package managers
which conda || which mamba  # At least one should exist
```

## Installation Steps

### 1. Environment Creation
- [ ] Navigate to project directory: `cd cyclicboltz1_mcp`
- [ ] Create conda environment: `mamba env create -f environment.yml` (or create manually)
- [ ] Activate environment: `mamba activate ./env` or `conda activate ./env`
- [ ] Verify Python path: `which python` (should point to env/bin/python)

### 2. Python Dependencies
- [ ] Install FastMCP: `pip install fastmcp loguru`
- [ ] Verify FastMCP: `python -c "from fastmcp import FastMCP; print('OK')"`
- [ ] Verify Loguru: `python -c "from loguru import logger; print('OK')"`

### 3. Server Registration
```bash
# Get absolute paths
PROJECT_DIR=$(pwd)
PYTHON_PATH=$(which python)

# Register MCP server
claude mcp add cycpep-tools -- $PYTHON_PATH $PROJECT_DIR/src/server.py
```

- [ ] Registration successful (no errors)
- [ ] Verify registration: `claude mcp list`
- [ ] Server shows as "cycpep-tools"
- [ ] Connection status shows "✓ Connected"

## Validation Tests

### 1. Automated Integration Tests
- [ ] Run integration tests: `python tests/run_integration_tests.py`
- [ ] All tests pass (100% pass rate)
- [ ] No critical issues reported
- [ ] Reports generated in `reports/` directory

### 2. Functional Validation
- [ ] Run functional tests: `python tests/functional_validation.py`
- [ ] All 5 test categories pass
- [ ] No import errors
- [ ] Job manager works correctly

### 3. Manual Server Validation
```bash
# Test server imports
python -c "from src.server import mcp; print('Server OK')"

# Test job manager
python -c "from src.jobs.manager import job_manager; print('Job manager OK')"

# Test server startup (Ctrl+C to exit)
fastmcp dev src/server.py
```

- [ ] Server imports without errors
- [ ] Job manager initializes correctly
- [ ] Server starts in development mode
- [ ] No runtime exceptions during startup

## Tool Discovery Validation

### Using Claude Code
Start Claude Code and test each tool category:

#### Server Information
- [ ] Ask: "What MCP tools are available for cyclic peptides?"
- [ ] Response lists 10 tools across 3 categories
- [ ] Ask: "What are the capabilities of the cycpep-tools server?"
- [ ] Response shows server info, limitations, and capabilities

#### Sequence Validation
- [ ] Ask: "Validate the sequence 'GRGDSP' for cyclic peptide prediction"
- [ ] Response shows valid=true, length=6, no issues
- [ ] Ask: "Validate the sequence 'GRGDXP' (invalid amino acid)"
- [ ] Response shows valid=false, reports invalid amino acid X

#### Job Submission
- [ ] Ask: "Submit a structure prediction job for 'GRGDSP'"
- [ ] Response returns job_id (8 characters)
- [ ] Response includes status tracking instructions

#### Job Management
- [ ] Ask: "List all submitted jobs"
- [ ] Response shows job list (may be empty initially)
- [ ] Ask: "Check status of job [job_id]"
- [ ] Response shows job details and current status

## Error Handling Validation

### Invalid Inputs
- [ ] Empty sequence validation fails gracefully
- [ ] Invalid amino acids are caught and reported
- [ ] Non-existent job IDs return proper error messages
- [ ] Invalid job operations return helpful errors

### Edge Cases
- [ ] Very long sequences (>100 AA) show warnings
- [ ] Special characters in job names are handled
- [ ] Concurrent job submissions work correctly
- [ ] Server restart preserves job history

## File System Validation

### Required Directories
- [ ] `jobs/` directory exists and is writable
- [ ] `scripts/` directory contains all 4 prediction scripts
- [ ] `tests/` directory contains test files
- [ ] `reports/` directory contains test results

### Script Files
- [ ] `scripts/predict_structure.py` exists and compiles
- [ ] `scripts/predict_multimer.py` exists and compiles
- [ ] `scripts/predict_affinity.py` exists and compiles
- [ ] `scripts/predict_modified.py` exists and compiles

### Configuration Files
- [ ] `src/server.py` imports without errors
- [ ] `src/jobs/manager.py` imports without errors
- [ ] All Python files have correct syntax

## Performance Validation

### Response Times
- [ ] Tool discovery: < 1 second
- [ ] Job submission: < 2 seconds
- [ ] Status checks: < 1 second
- [ ] List operations: < 1 second

### Concurrency
- [ ] Multiple job submissions work simultaneously
- [ ] Job status checks work during submissions
- [ ] No race conditions in job management

## Documentation Validation

### Generated Reports
- [ ] `reports/step7_integration.md` exists and shows all tests passed
- [ ] `reports/step7_comprehensive_results.md` exists and shows summary
- [ ] `tests/test_prompts.md` exists with 30 test scenarios

### Usage Instructions
- [ ] README.md updated with installation instructions
- [ ] Test prompts are clear and actionable
- [ ] Error messages are helpful and specific

## Real-World Scenario Testing

### End-to-End Workflow
Test this complete workflow:

1. **Validation Phase**
   - [ ] Validate sequence: "GRGDSP"
   - [ ] Confirm sequence is valid for prediction

2. **Submission Phase**
   - [ ] Submit structure prediction job
   - [ ] Receive job_id successfully

3. **Monitoring Phase**
   - [ ] Check job status multiple times
   - [ ] View job logs (if available)
   - [ ] List all jobs to see submission

4. **Management Phase**
   - [ ] Cancel job if needed
   - [ ] Verify cancellation worked

### Multi-Job Scenario
- [ ] Submit 3 different jobs simultaneously
- [ ] Track all jobs using list_jobs
- [ ] Check individual job statuses
- [ ] Verify no job ID conflicts

## Production Readiness Checklist

### Security
- [ ] No shell injection vulnerabilities
- [ ] Input validation on all parameters
- [ ] Safe file path handling
- [ ] Process isolation for jobs

### Reliability
- [ ] Error recovery mechanisms work
- [ ] Job persistence across server restarts
- [ ] Graceful handling of resource constraints
- [ ] Proper cleanup of failed jobs

### Monitoring
- [ ] Job execution logs are accessible
- [ ] Server status can be monitored
- [ ] Failed jobs provide diagnostic information
- [ ] Performance metrics are trackable

## Final Sign-Off

### Integration Success Criteria
- [ ] All automated tests pass (18/18)
- [ ] Claude Code shows server as "✓ Connected"
- [ ] All 10 tools are discoverable and callable
- [ ] Job workflow (submit → status → result) works end-to-end
- [ ] Error handling provides helpful feedback
- [ ] Performance is acceptable for research use

### Documentation Complete
- [ ] Installation instructions are clear
- [ ] Test scenarios cover all major use cases
- [ ] Known limitations are documented
- [ ] Usage examples are provided

### Ready for Use
- [ ] Scientists can use tools through natural language
- [ ] Job management supports research workflows
- [ ] Error messages guide users effectively
- [ ] Performance scales for typical research loads

## Quick Commands Reference

```bash
# Test server health
claude mcp list | grep cycpep-tools

# Run all validation tests
python tests/run_integration_tests.py
python tests/functional_validation.py

# Start development server
fastmcp dev src/server.py

# Check job directory
ls -la jobs/

# View test results
cat reports/step7_integration.md
```

---

**✅ VALIDATION COMPLETE**: If all checkboxes are marked, the Cyclic Peptide MCP server is successfully installed, integrated with Claude Code, and ready for production use in research and development workflows.