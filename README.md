# GenBank SeqKit

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Build Status](https://github.com/<yourusername>/genbank_seqkit/actions/workflows/main.yml/badge.svg)](https://github.com/newmanreb/genbank_seqkit/actions)
[![Coverage Status](https://codecov.io/gh/<yourusername>/genbank_seqkit/branch/main/graph/badge.svg?token=<CODECOV_TOKEN>)](https://codecov.io/gh/newmanreb/genbank_seqkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Version 1.0**

A Python toolkit for fetching, parsing, and formatting **GenBank transcript records** via the NCBI Entrez API.

---

## Overview

**GenBank SeqKit** provides tools to:

- Fetch transcript records from the NCBI Nucleotide database.
- Parse and store relevant metadata, including gene symbol, HGNC ID, DNA/RNA/protein sequences.
- Generate FASTA and simplified GenBank-like outputs.
- Provide detailed logging for debugging and research workflows.

The core of this toolkit is the `Transcript` class, which encapsulates a GenBank transcript as a Python object.



Entrez API fetch module courtesy of Peter Freeman: 
https://github.com/Peter-J-Freeman/SeqKitSTP2025/blob/develop/SeqToolkit/utils/entrez_efetch.py
