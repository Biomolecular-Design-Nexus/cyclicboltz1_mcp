# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-31
- **Filter Applied**: cyclic peptide structure prediction using CyclicBoltz1, non-canonical amino acid support, cyclic peptide monomer and multimer prediction
- **Python Version**: 3.10.19
- **Environment Strategy**: single environment (./env)

## Use Cases

### UC-001: Cyclic Peptide Structure Prediction
- **Description**: Predict 3D structure of individual cyclic peptides using the `cyclic: true` flag in Boltz
- **Script Path**: `examples/use_case_1_cyclic_peptide_structure.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env`
- **Source**: `repo/boltz/examples/cyclic_prot.yaml`, documentation in prediction.md

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Cyclic peptide amino acid sequence | --sequence, -s |
| model | choice | Boltz model (boltz1/boltz2) | --model, -m |
| output_dir | path | Output directory for results | --output_dir, -o |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| structure_cif | file | 3D structure in mmCIF format |
| confidence_json | file | pLDDT and TM-score confidence metrics |
| pae_npz | file | Predicted Aligned Error matrix |

**Example Usage:**
```bash
python examples/use_case_1_cyclic_peptide_structure.py --sequence "QLEDSEVEAVAKG" --model boltz2
```

**Example Data**: `examples/data/cyclic_prot.yaml`

---

### UC-002: Cyclic Peptide Multimer Prediction
- **Description**: Predict structures and interactions of multiple cyclic peptides (homo/heteromultimers)
- **Script Path**: `examples/use_case_2_cyclic_peptide_multimer.py`
- **Complexity**: complex
- **Priority**: high
- **Environment**: `./env`
- **Source**: `repo/boltz/examples/multimer.yaml`, adapted for cyclic peptides

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequences | list | Multiple cyclic peptide sequences | --sequences, -s |
| chain_ids | list | Chain identifiers for each peptide | --chain_ids, -c |
| model | choice | Boltz model (boltz1/boltz2) | --model, -m |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| complex_structure | file | Multimer 3D structure |
| interface_scores | file | Interface quality metrics (iptm) |
| interaction_analysis | file | Chain-pair interaction confidence |

**Example Usage:**
```bash
python examples/use_case_2_cyclic_peptide_multimer.py --sequences "QLEDSEVEAVAKG" "MKLFWDESG" --chain_ids "A" "B"
```

**Example Data**: `examples/data/multimer.yaml` (adapted for cyclic peptides)

---

### UC-003: Cyclic Peptide-Target Binding Affinity
- **Description**: Predict binding affinity between cyclic peptides and target proteins using Boltz-2
- **Script Path**: `examples/use_case_3_cyclic_peptide_affinity.py`
- **Complexity**: complex
- **Priority**: high
- **Environment**: `./env`
- **Source**: `repo/boltz/examples/affinity.yaml`, documentation on affinity prediction

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| peptide | string | Cyclic peptide sequence | --peptide, -p |
| target | string | Target protein sequence | --target, -t |
| output_dir | path | Results directory | --output_dir, -o |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| affinity_json | file | IC50 and binding probability predictions |
| complex_structure | file | Bound complex 3D structure |
| binding_analysis | file | Detailed affinity metrics and interpretation |

**Example Usage:**
```bash
python examples/use_case_3_cyclic_peptide_affinity.py --peptide "QLEDSEVEAVAKG" --target "MKLLVASILALAVCSGSAKETTVLTLSDQGKFSL..."
```

**Example Data**: `examples/data/affinity.yaml`

---

### UC-004: Non-canonical Amino Acid Support
- **Description**: Structure prediction of cyclic peptides with modified/non-canonical amino acids via CCD codes
- **Script Path**: `examples/use_case_4_noncanonical_amino_acids.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env`
- **Source**: Boltz modification support in prediction.md, CCD code documentation

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Base peptide sequence (canonical AA) | --sequence, -s |
| modifications | string | Position:modification pairs | --modifications, -m |
| model | choice | Boltz model (boltz2 recommended) | --model |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| modified_structure | file | 3D structure with modifications |
| confidence_scores | file | Confidence at modification sites |
| modification_analysis | file | Impact of modifications on structure |

**Example Usage:**
```bash
python examples/use_case_4_noncanonical_amino_acids.py --sequence "QLEDSEVEAVAKG" --modifications "3:phosphoserine,7:hydroxyproline"
```

**Example Data**: Built-in modification library (phosphoserine, hydroxyproline, etc.)

---

## Summary

| Metric | Count |
|--------|-------|
| Total Found | 4 |
| Scripts Created | 4 |
| High Priority | 4 |
| Medium Priority | 0 |
| Low Priority | 0 |
| Demo Data Copied | Yes |

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/boltz/examples/cyclic_prot.yaml` | `examples/data/cyclic_prot.yaml` | Basic cyclic peptide configuration |
| `repo/boltz/examples/affinity.yaml` | `examples/data/affinity.yaml` | Protein-ligand affinity example |
| `repo/boltz/examples/multimer.yaml` | `examples/data/multimer.yaml` | Multimer prediction example |
| `repo/boltz/examples/ligand.yaml` | `examples/data/ligand.yaml` | Protein-ligand complex |
| `repo/boltz/examples/pocket.yaml` | `examples/data/pocket.yaml` | Pocket constraint example |
| `repo/boltz/examples/msa/seq1.a3m` | `examples/data/msa/seq1.a3m` | Multiple sequence alignment |
| `repo/boltz/examples/msa/seq2.a3m` | `examples/data/msa/seq2.a3m` | Additional MSA file |

## Technical Features Implemented

### Cyclic Peptide Support
- ✅ `cyclic: true` flag properly implemented in YAML generation
- ✅ Single peptide structure prediction
- ✅ Multimer complex formation
- ✅ Interface analysis for peptide-peptide interactions

### Model Compatibility
- ✅ Boltz-1 support for structure prediction
- ✅ Boltz-2 support for structure + affinity prediction
- ✅ Automatic model selection based on task requirements
- ✅ CPU and GPU acceleration modes

### Non-canonical Amino Acids
- ✅ CCD code integration for modifications
- ✅ Common modification library (phosphorylation, methylation, etc.)
- ✅ Position-specific modification mapping
- ✅ Validation of modification positions

### Input/Output Handling
- ✅ YAML configuration generation
- ✅ Command-line argument parsing
- ✅ Result file organization and interpretation
- ✅ Comprehensive error handling

### Scientific Accuracy
- ✅ Proper confidence score interpretation
- ✅ Affinity value conversion (IC50, pIC50)
- ✅ Interface quality assessment
- ✅ Ensemble prediction averaging

## Use Case Complexity Analysis

### Simple Tasks
None identified - all cyclic peptide tasks require some complexity

### Medium Complexity
- Single cyclic peptide structure prediction
- Modified peptide prediction

### High Complexity
- Multimer prediction and interface analysis
- Binding affinity prediction with target proteins

## Future Enhancements

### Potential Additional Use Cases
1. **Peptide Library Screening**: Batch prediction on multiple sequences
2. **Drug-Target Selectivity**: Cross-reactivity analysis with protein families
3. **Conformational Dynamics**: Multiple conformer generation and analysis
4. **Peptide Design Optimization**: Structure-guided sequence modification

### Technical Improvements
1. **Constraint-based Prediction**: Distance and angle constraints
2. **Template-guided Modeling**: Using known cyclic peptide structures
3. **Ensemble Analysis**: Statistical analysis across multiple predictions
4. **Visualization Integration**: 3D structure viewing and analysis tools