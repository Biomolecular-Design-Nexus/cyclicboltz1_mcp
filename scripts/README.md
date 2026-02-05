# MCP Scripts

Clean, self-contained scripts extracted from cyclic peptide use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (standard library only: `argparse`, `os`, `subprocess`, `tempfile`, `yaml`, `json`, `pathlib`)
2. **Self-Contained**: Functions inlined where possible, no repo dependencies
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Independent | Config |
|--------|-------------|-------------|--------|
| `predict_structure.py` | Predict 3D structure of cyclic peptide | Yes | `../configs/predict_structure_config.json` |
| `predict_multimer.py` | Predict cyclic peptide multimers | Yes | `../configs/predict_multimer_config.json` |
| `predict_affinity.py` | Predict peptide-target affinity (⚠️ Limited) | Yes | `../configs/predict_affinity_config.json` |
| `predict_modified.py` | Predict modified peptide structures | Yes | `../configs/predict_modified_config.json` |

## Dependencies Status

All scripts are **fully independent** with minimal dependencies:

- ✅ **No external scientific packages required** (numpy, rdkit, torch, etc.)
- ✅ **No repo code dependencies** (all functions inlined)
- ✅ **Only standard library imports**
- ✅ **Configuration externalized**

## Usage

### Basic Usage

```bash
# Activate environment
mamba activate ./env  # or: conda activate ./env

# Predict single cyclic peptide structure
python scripts/predict_structure.py --input "QLEDSEVEAVAKG" --output results/structure

# Predict multimer (two peptides)
python scripts/predict_multimer.py --sequences "QLEDSEVEAVAKG" "MKLFWDESG" --output results/multimer

# Predict with modifications
python scripts/predict_modified.py --sequence "QLEDSEVEAVAKG" --modifications "3:phosphoserine,7:hydroxyproline" --output results/modified

# List available modifications
python scripts/predict_modified.py --list-modifications
```

### With Configuration Files

```bash
# Using custom config
python scripts/predict_structure.py --input "ACDEFGH" --config configs/predict_structure_config.json --output results/custom

# Override specific parameters
python scripts/predict_structure.py --input "ACDEFGH" --model boltz2 --samples 3 --output results/enhanced
```

## Configuration Files

Each script has a corresponding configuration file in `../configs/`:

- `predict_structure_config.json` - Structure prediction settings
- `predict_multimer_config.json` - Multimer prediction settings
- `predict_affinity_config.json` - Affinity prediction settings
- `predict_modified_config.json` - Modified peptide settings

Configuration files include:
- Model selection (boltz1 vs boltz2)
- Processing parameters (samples, recycling steps)
- Hardware settings (CPU/GPU)
- Validation options
- Example inputs

## Shared Library

Common functions are in `lib/`:
- `validation.py`: Input validation utilities
- `config.py`: Configuration file handling
- `boltz.py`: Boltz command execution
- `utils.py`: General utilities (chain IDs, formatting)

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped:

```python
# Structure prediction
from scripts.predict_structure import run_predict_structure

@mcp.tool()
def predict_cyclic_peptide_structure(sequence: str, output_dir: str = None):
    return run_predict_structure(sequence, output_dir)

# Multimer prediction
from scripts.predict_multimer import run_predict_multimer

@mcp.tool()
def predict_cyclic_peptide_multimer(sequences: list, output_dir: str = None):
    return run_predict_multimer(sequences, output_dir)
```

## Function Signatures

### `run_predict_structure(input_sequence, output_dir=None, config=None, **kwargs)`
- **Input**: Single peptide sequence
- **Output**: Structure prediction results
- **Returns**: Dict with success status, output files, metadata

### `run_predict_multimer(input_sequences, output_dir=None, chain_ids=None, config=None, **kwargs)`
- **Input**: List of peptide sequences
- **Output**: Multimer prediction results
- **Returns**: Dict with success status, output files, metadata

### `run_predict_affinity(peptide_sequence, target_sequence, output_dir=None, config=None, **kwargs)`
- **Input**: Peptide and target protein sequences
- **Output**: Affinity prediction results
- **Returns**: Dict with success status, affinity analysis, metadata
- **⚠️ Note**: May fail due to Boltz limitation with peptide-peptide interactions

### `run_predict_modified(input_sequence, modifications=None, output_dir=None, config=None, **kwargs)`
- **Input**: Base sequence and modification specification
- **Output**: Modified peptide structure prediction
- **Returns**: Dict with success status, output files, metadata

## Limitations and Notes

### Known Issues from Step 4 Testing

1. **⚠️ Boltz Dependency Missing**: All predictions will fail due to missing `cuequivariance_ops_torch` package
2. **⚠️ Affinity Limitation**: Boltz only supports small molecule ligands, not peptide-peptide affinity
3. **✅ Configuration Works**: YAML generation and CLI interfaces work correctly

### What Works

- ✅ Input validation and sequence processing
- ✅ YAML configuration generation
- ✅ Command-line interfaces and help
- ✅ Configuration file loading
- ✅ Error handling and reporting
- ✅ Output directory management

### What Will Fail (Due to Boltz Issues)

- ❌ Actual structure prediction (missing dependency)
- ❌ Peptide-peptide affinity prediction (functional limitation)

## Testing

Scripts have been tested for:
- ✅ Python syntax validation
- ✅ CLI argument parsing
- ✅ Function call interfaces
- ✅ Configuration handling
- ✅ Input validation
- ✅ Output directory creation

## Example Configurations

### Structure Prediction
```json
{
  "model": {"name": "boltz1"},
  "processing": {
    "accelerator": "cpu",
    "diffusion_samples": 1,
    "recycling_steps": 3,
    "use_msa_server": true
  }
}
```

### Multimer Prediction
```json
{
  "model": {"name": "boltz1"},
  "processing": {
    "diffusion_samples": 3,
    "recycling_steps": 5
  },
  "multimer": {
    "auto_chain_ids": true,
    "min_chains": 2
  }
}
```

### Modified Peptides
```json
{
  "model": {"name": "boltz2"},
  "modifications": {
    "supported_types": {
      "phosphorylation": ["phosphoserine", "phosphothreonine"],
      "d_amino_acids": ["d_alanine", "d_valine"]
    }
  }
}
```

## Future MCP Integration

These scripts are designed for easy MCP tool wrapping:

1. **Function-based**: Each script exports a main function
2. **JSON serializable**: All inputs/outputs are JSON-compatible
3. **Error handling**: Consistent error reporting structure
4. **Documentation**: Inline docstrings for MCP tool descriptions
5. **Validation**: Input validation with clear error messages

Ready for Step 6: MCP tool wrapper creation!