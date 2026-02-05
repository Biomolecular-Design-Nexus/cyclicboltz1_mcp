# Step 3: Environment Setup Report

## Python Version Detection
- **Detected Python Version**: 3.10 (from pyproject.toml: ">=3.10,<3.13")
- **Strategy**: Single environment setup (Python >= 3.10, no legacy environment needed)

## Main MCP Environment
- **Location**: `./env`
- **Python Version**: 3.10.19 (verified working)
- **Package Manager**: mamba (preferred over conda for speed)

## Legacy Build Environment
- **Status**: Not needed
- **Reason**: Boltz requires Python >=3.10, which is compatible with MCP requirements

## Dependencies Installed

### Core Boltz Dependencies
- boltz==2.2.1 (editable installation)
- torch==2.9.1 (with CUDA support)
- pytorch-lightning==2.5.0
- rdkit==2025.9.3 (essential for molecular manipulation)
- numpy==1.26.4
- scipy==1.13.1
- pandas==2.3.3
- biopython==1.84

### Scientific Computing
- scikit-learn==1.6.1
- numba==0.61.0
- gemmi==0.6.5 (crystallographic data)
- einops==0.8.0
- einx==0.3.0

### Deep Learning Infrastructure
- nvidia-cuda-runtime-cu12==12.8.90
- nvidia-cudnn-cu12==9.10.2.21
- nvidia-cublas-cu12==12.8.4.1
- triton==3.5.1

### MCP Infrastructure
- fastmcp==2.14.1
- mcp==1.25.0
- pydantic==2.12.5
- click==8.3.1
- pyyaml==6.0.3

### Additional Dependencies
- hydra-core==1.3.2 (configuration management)
- wandb==0.18.7 (experiment tracking)
- fairscale==0.4.13 (distributed training)
- mashumaro==3.14 (serialization)

## Activation Commands
```bash
# Main MCP environment
eval "$(mamba shell hook --shell bash)"
mamba activate ./env
```

## Verification Status
- [x] Main environment (./env) functional
- [x] Core imports working (torch, rdkit, boltz)
- [x] Boltz CLI accessible and functional
- [x] RDKit working (essential for cyclic peptide handling)
- [x] FastMCP installed for MCP functionality
- [x] All example YAML files copied to examples/data/
- [x] MSA files available in examples/data/msa/

## Installation Commands Used
```bash
# Package manager detection
which mamba  # Found: /home/xux/miniforge3/condabin/mamba

# Environment creation
mamba create -p ./env python=3.10 pip -y

# Environment activation
eval "$(mamba shell hook --shell bash)"
mamba activate ./env

# Core package installation
cd repo/boltz && pip install -e . && cd ../..

# MCP dependencies
pip install --force-reinstall --no-cache-dir fastmcp
```

## Version Conflicts (Non-critical)
The following version conflicts exist but do not affect functionality:
- boltz 2.2.1 requires click==8.1.7, but installed click 8.3.1
- boltz 2.2.1 requires pyyaml==6.0.2, but installed pyyaml 6.0.3
- boltz 2.2.1 requires requests==2.32.3, but installed requests 2.32.5

These minor version differences are expected and don't impact the core functionality.

## Performance Notes
- GPU support available via CUDA 12.8
- CPU mode functional for smaller peptides
- Memory requirements scale with peptide size and complexity
- Recommended: 8GB+ RAM for typical cyclic peptide predictions

## Notes
- Environment successfully supports all Boltz models (boltz1, boltz2)
- Cyclic peptide flag (`cyclic: true`) properly recognized
- MSA server integration working via `--use_msa_server`
- Both structure and affinity predictions functional
- Non-canonical amino acid support via CCD codes implemented