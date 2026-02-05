# Comprehensive Test Prompts for Cyclic Peptide MCP Server

## Pre-Testing Checklist
- [ ] MCP server registered: `claude mcp list` shows cycpep-tools
- [ ] Server health check shows ✓ Connected
- [ ] Test environment activated

## Tool Discovery Tests

### Test 1: List All Available Tools
**Prompt:**
```
What MCP tools are available for cyclic peptides? List them with brief descriptions of what each tool does.
```

**Expected Response:**
- Should list 10 tools: get_job_status, get_job_result, get_job_log, cancel_job, list_jobs, submit_structure_prediction, submit_multimer_prediction, submit_affinity_prediction, submit_modified_peptide_prediction, list_available_modifications, validate_peptide_sequence, get_server_info

### Test 2: Get Server Information
**Prompt:**
```
What information can you tell me about the cycpep-tools MCP server? What are its capabilities and limitations?
```

**Expected Response:**
- Server version and description
- List of capabilities (structure prediction, multimer prediction, etc.)
- API types (submit, job management)
- Known limitations

## Validation Tools Tests

### Test 3: Sequence Validation - Valid Sequence
**Prompt:**
```
Validate the amino acid sequence "GRGDSP" for cyclic peptide structure prediction.
```

**Expected Response:**
- Status: success
- Valid: true
- Sequence length: 6
- No issues found

### Test 4: Sequence Validation - Invalid Characters
**Prompt:**
```
Validate this peptide sequence: "GRGDXP" (contains invalid amino acid X)
```

**Expected Response:**
- Status: success
- Valid: false
- Issues: Invalid amino acids: X

### Test 5: Sequence Validation - Too Short
**Prompt:**
```
Validate this peptide sequence: "GR" (only 2 amino acids)
```

**Expected Response:**
- Status: success
- Valid: false
- Issues: Sequence too short (minimum 3 residues)

### Test 6: Available Modifications
**Prompt:**
```
What non-canonical amino acid modifications are available for cyclic peptide prediction?
```

**Expected Response:**
- List of available modifications with descriptions
- Information about how to specify them

## Job Management Tests

### Test 7: List Jobs (Initially Empty)
**Prompt:**
```
List all cyclic peptide computation jobs currently submitted.
```

**Expected Response:**
- Status: success
- Jobs: empty list initially
- Total: 0

### Test 8: Submit Structure Prediction Job
**Prompt:**
```
Submit a 3D structure prediction job for the cyclic peptide with sequence "GRGDSP".
```

**Expected Response:**
- Status: submitted
- job_id: 8-character string
- Message with instructions to check status

### Test 9: Check Job Status
**Prompt:**
```
Check the status of job [job_id from Test 8].
```

**Expected Response:**
- job_id matches
- status: pending, running, or completed
- Timestamps for submitted_at, started_at

### Test 10: View Job Logs
**Prompt:**
```
Show me the last 20 lines of logs for job [job_id from Test 8].
```

**Expected Response:**
- Status: success or error if log doesn't exist yet
- Log lines if available
- Total line count

### Test 11: List Jobs After Submission
**Prompt:**
```
List all submitted jobs and show their current status.
```

**Expected Response:**
- At least one job (from Test 8)
- Job details including status and submission time

## Submit API Tests (Long-Running)

### Test 12: Submit Multimer Prediction
**Prompt:**
```
Submit a multimer structure prediction job for these cyclic peptides: "GRGDSP" and "RGDFV".
```

**Expected Response:**
- Job submitted successfully
- job_id returned
- Instructions for status checking

### Test 13: Submit Modified Peptide Prediction
**Prompt:**
```
Submit a structure prediction job for the cyclic peptide "GRGDSP" with modifications at position 3 (phosphoserine).
```

**Expected Response:**
- Job submitted successfully
- Modified peptide parameters accepted

### Test 14: Submit Affinity Prediction (Known Limitation)
**Prompt:**
```
Submit a binding affinity prediction job between the cyclic peptide "GRGDSP" and a target protein "MKFLVLGIGV".
```

**Expected Response:**
- Job submitted (may fail during execution)
- Warning about known limitations
- job_id returned

## Error Handling Tests

### Test 15: Invalid Job ID
**Prompt:**
```
Check the status of job "invalid123".
```

**Expected Response:**
- Status: error
- Error message: Job invalid123 not found

### Test 16: Get Results of Non-Existent Job
**Prompt:**
```
Get the results for job "nonexistent".
```

**Expected Response:**
- Status: error
- Error: Job not found

### Test 17: Cancel Non-Running Job
**Prompt:**
```
Cancel job "notrunning123".
```

**Expected Response:**
- Status: error
- Error: Job not running or not found

## Batch Processing Scenarios

### Test 18: Multiple Job Submissions
**Prompt:**
```
Submit structure prediction jobs for these three cyclic peptides:
1. "GRGDSP"
2. "RGDFV"
3. "YIGSR"

Then list all jobs to see their status.
```

**Expected Response:**
- Three separate job submissions
- Three job_ids returned
- List shows all three jobs

### Test 19: Filter Jobs by Status
**Prompt:**
```
List all jobs with status "pending".
```

**Expected Response:**
- Filtered list showing only pending jobs
- Status field matches filter

## Real-World Scenarios

### Test 20: End-to-End Workflow
**Prompt:**
```
I want to predict the 3D structure of the cyclic peptide GRGDSP. First validate the sequence, then submit the job, check its status, and explain how to get the results when it's done.
```

**Expected Response:**
- Sequence validation passes
- Job submitted successfully
- Status check shows job details
- Clear instructions for getting results

### Test 21: Drug-like Assessment Workflow
**Prompt:**
```
I'm developing a cyclic peptide drug candidate with sequence "KLVFFAED". Help me:
1. Validate the sequence for structure prediction
2. Submit a 3D structure prediction job
3. Check what happens if the sequence were modified with a phosphoserine at position 2
```

**Expected Response:**
- Sequence validation
- Structure prediction job submission
- Modified peptide job submission with proper modification syntax

### Test 22: Research Screening Workflow
**Prompt:**
```
I need to screen a small library of cyclic peptides for my research. Submit jobs for these candidates:
- "GRGDSP" (control)
- "KLDLKLDL" (experimental design 1)
- "PRGLKLDL" (experimental design 2)

Then show me how to track all of them.
```

**Expected Response:**
- Three job submissions
- job_ids for tracking
- Demonstration of list_jobs functionality

## Performance and Load Tests

### Test 23: Rapid Job Submission
**Prompt:**
```
Submit 5 structure prediction jobs quickly for these sequences:
"GRG", "DSPK", "LVFF", "AEDKL", "GRGDS"

Then list all jobs to see if they were all registered properly.
```

**Expected Response:**
- All 5 jobs submitted successfully
- All job_ids returned
- List shows all 5 jobs

### Test 24: Job Queue Management
**Prompt:**
```
Check the status of all my submitted jobs, then show me logs for any that are currently running.
```

**Expected Response:**
- Status of all jobs
- Logs for running jobs (if any)

## Edge Cases and Error Recovery

### Test 25: Empty Sequence
**Prompt:**
```
Submit a structure prediction job for an empty sequence: ""
```

**Expected Response:**
- Validation should fail
- Clear error message about empty sequence

### Test 26: Very Long Sequence
**Prompt:**
```
Validate this very long peptide sequence for structure prediction: "GRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSPGRGDSP"
```

**Expected Response:**
- Warning about long sequence (>100 residues)
- May be slow warning

### Test 27: Special Characters in Job Name
**Prompt:**
```
Submit a structure prediction job for "GRGDSP" with the job name "test-job_with@special#chars".
```

**Expected Response:**
- Job submission handles special characters gracefully
- job_id returned successfully

## Integration Verification Tests

### Test 28: Tool Availability Check
**Prompt:**
```
Can you use the cycpep-tools to help me? What specific actions can you perform?
```

**Expected Response:**
- Confirmation that tools are available
- List of specific capabilities
- Examples of what can be done

### Test 29: Error Message Quality
**Prompt:**
```
Try to get results for a job that doesn't exist and show me what error message you receive.
```

**Expected Response:**
- Clear, helpful error message
- Guidance on next steps

### Test 30: Documentation and Help
**Prompt:**
```
How do I use the cyclic peptide tools? Explain the workflow from sequence to 3D structure.
```

**Expected Response:**
- Clear workflow explanation
- Step-by-step instructions
- Examples with actual tool calls

## Success Criteria Summary

For each test, verify:
- ✅ Tool executes without errors
- ✅ Response format matches expected structure
- ✅ Error handling provides helpful messages
- ✅ Job IDs are properly formatted (8 characters)
- ✅ Status values are valid enum values
- ✅ Timestamps are in ISO format
- ✅ File paths and directories are handled correctly
- ✅ Sequence validation catches common errors
- ✅ Submit operations return proper job tracking info
- ✅ Job management operations work as expected

## Notes for Testers

1. **Job Execution**: Remember that actual Boltz execution requires GPU resources and proper environment setup. Jobs may fail due to missing dependencies, but the MCP layer should handle this gracefully.

2. **Timing**: Structure prediction jobs are designed to run for 10+ minutes. Don't expect immediate completion.

3. **Error States**: Some tools (like affinity prediction) have known limitations. Verify that these are properly communicated to users.

4. **Concurrency**: Test that multiple jobs can be submitted and tracked simultaneously.

5. **Cleanup**: After testing, you may want to clear the jobs directory: `rm -rf jobs/*`