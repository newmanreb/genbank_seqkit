# GenBank SeqKit

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Build Status](https://github.com/newmanreb/genbank_seqkit/actions/workflows/main.yml/badge.svg)](https://github.com/newmanreb/genbank_seqkit/actions)
[![Coverage Status](https://codecov.io/gh/newmanreb/genbank_seqkit/branch/main/graph/badge.svg?token=547d98fc-a33b-4e55-a3b6-eda0e5c1255a)](https://codecov.io/gh/newmanreb/genbank_seqkit)

**Version 1.0**

A Python toolkit for fetching, parsing, and formatting **GenBank transcript records** via the NCBI Entrez API.

---

## Overview

**GenBank SeqKit** provides tools to:

- Fetch transcript records from the NCBI Nucleotide database.
- Parse and store relevant metadata, including gene symbol, HGNC ID, DNA/RNA/protein sequences.
- Generate FASTA and simplified GenBank-like outputs.
- Provide detailed logging for debugging and research workflows.

---

## Features 

- **Automatic NCBI fetch**: Provide a RefSeq transcript ID (e.g., `"NM_000093.5"`) and retrieve the full record.
- **Data parsing**: Extract DNA, RNA, protein sequences, gene symbol, HGNC ID, and more.
- **Output formats**: FASTA and simplified GenBank-style strings for sequences.
- **Verbose logging**: Optional debug messages to trace the fetching and parsing steps.
- **Easy refresh**: Re-fetch and update a transcript with a single method call.

---

## Installation 

```bash
# Clone repository
git clone https://github.com/<yourusername>/genbank_seqkit.git
cd genbank_seqkit

# Optional: create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Python 
```python
from genbank_seqkit.transcript import Transcript

# Create a Transcript object (automatically fetches from NCBI)
t = Transcript("NM_000093.5", verbose=True)

# Print summary
print(t)

# Get DNA sequence in FASTA format
fasta = t.as_fasta(seq_type="DNA")
print(fasta)

# Get GenBank-style output
genbank_str = t.as_genbank(seq_type="DNA")
print(genbank_str)

# Refresh transcript data
t.refresh(verbose=True)
```
### Command line 
```bash
python src/genbank_seqkit/main.py NM_000093.5
```

---

## Citations
- Entrez API fetch module courtesy of Peter Freeman: 
https://github.com/Peter-J-Freeman/SeqKitSTP2025/blob/develop/SeqToolkit/utils/entrez_efetch.py
- This code and documentation were generated with guidance from ChatGPT (GPT-5-mini), with all outputs manually verified for correctness and applicability to this project.