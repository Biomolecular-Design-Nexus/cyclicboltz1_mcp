#!/bin/bash
# Quick Setup Script for Boltz MCP (cyclicboltz1)
# Boltz: Biomolecular interaction prediction model family
# Boltz-1/2 approaches AlphaFold3 accuracy for structure and binding affinity prediction
# Source: https://github.com/jwohlwend/boltz

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up Boltz MCP ==="

# Step 1: Create Python environment
echo "[1/4] Creating Python 3.10 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.10 -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.10 -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env)

# Step 2: Install Boltz from repo
echo "[2/4] Installing Boltz..."
cd repo/boltz && ../../env/bin/pip install -e . && cd ../..

# Step 3: Install fastmcp and loguru
echo "[3/4] Installing fastmcp and loguru..."
./env/bin/pip install fastmcp loguru --ignore-installed

# Step 4: Install RDKit
echo "[4/4] Installing RDKit..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env -c conda-forge rdkit -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env -c conda-forge rdkit -y) || \
(echo "Warning: Neither mamba nor conda found, using pip for rdkit" && ./env/bin/pip install rdkit)

echo ""
echo "=== Boltz MCP Setup Complete ==="
echo "Usage: boltz predict input_path --use_msa_server"
echo "For CUDA support: pip install boltz[cuda]"
echo "To run the MCP server: ./env/bin/python src/server.py"
