import pytest
from genbank_seqkit.main import Transcript
from unittest.mock import patch

# Test that a Transcript object instantiates correctly
@patch("genbank_seqkit.main.Transcript._fetch_and_populate")
def test_transcript_init(mock_fetch):
    t = Transcript("NM_000093.5")
    mock_fetch.assert_called_once()
    assert t.transcript_id == "NM_000093.5"
    assert t.gene_symbol is None
    assert t.dna_sequence is None

# Test _fetch_and_populate() functionality with a fake API call
@patch("genbank_seqkit.main.fetch_transcript_record")
def test_fetch_and_populate_sets_attributes(mock_fetch):
    mock_fetch.return_value = {
        "GBSeq_accession-version": "NM_000093.5",
        "GBSeq_sequence": "atgc",
        "GBSeq_length": "4",
        "GBSeq_moltype": "mRNA",
        "GBSeq_definition": "Fake gene record",
        "GBSeq_feature-table": {
            "GBFeature": [{
                "GBFeature_key": "gene",
                "GBFeature_quals": {
                    "GBQualifier": [
                        {"GBQualifier_name": "gene", "GBQualifier_value": "COL5A1"},
                        {"GBQualifier_name": "db_xref", "GBQualifier_value": "HGNC:2187"}
                    ]
                }
            }]
        }
    }

    t = Transcript("NM_000093.5")
    assert t.gene_symbol == "COL5A1"
    assert t.hgnc_id == "2187"

# Test FASTA format without API calling
def test_as_fasta_returns_expected_format():
    t = Transcript.__new__(Transcript)  # bypass __init__ to skip fetching
    t.transcript_id = "NM_000093.5"
    t.dna_sequence = "ATGC"
    fasta = t.as_fasta(seq_type="DNA")
    assert fasta.startswith(">NM_000093.5 | DNA")
    assert "ATGC" in fasta

# Test GenBank formatting without API calling
def test_as_genbank_contains_locus_and_origin():
    t = Transcript.__new__(Transcript)
    t.transcript_id = "NM_000093.5"
    t.dna_sequence = "ATGC"
    gb = t.as_genbank(seq_type="DNA")
    assert "LOCUS" in gb
    assert "ORIGIN" in gb

# Test error handling in as_fasta()
def test_as_fasta_raises_for_unknown_type():
    t = Transcript.__new__(Transcript)
    t.transcript_id = "NM_000093.5"
    with pytest.raises(ValueError):
        t.as_fasta(seq_type="invalid")

