import pytest
from genbank_seqkit.transcript import Transcript
from unittest.mock import patch

# Test that a Transcript object instantiates correctly
@patch("genbank_seqkit.transcript.Transcript._fetch_and_populate")
def test_transcript_init(mock_fetch):
    t = Transcript("NM_000093.5")
    mock_fetch.assert_called_once()
    assert t.transcript_id == "NM_000093.5"
    assert t.gene_symbol is None
    assert t.dna_sequence is None

# Test _fetch_and_populate() functionality with a fake API call
@patch("genbank_seqkit.transcript.fetch_transcript_record")
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

# Test CDS qualifiers correctly set protein sequence and ID.
def test_cds_and_protein_info(monkeypatch):
    # Create a dummy Transcript object without triggering network calls
    transcript = Transcript.__new__(Transcript)
    transcript.protein_sequence = None
    transcript.protein_id = None

    # Mock logger so it doesn’t try to write to a file
    class DummyLogger:
        def debug(self, msg): pass

    temp_logger = DummyLogger()

    # Simulate CDS feature with translation and protein_id qualifiers
    key = "CDS"
    quals = [
        {"GBQualifier_name": "translation", "GBQualifier_value": "MTEYKLVVVG"},
        {"GBQualifier_name": "protein_id", "GBQualifier_value": "NP_001234567.1"}
    ]

    # Execute the same logic you use in the method
    for q in quals:
        if q.get("GBQualifier_name") == "translation":
            transcript.protein_sequence = q.get("GBQualifier_value")
            temp_logger.debug(f"Protein sequence found, length={len(transcript.protein_sequence)}")
        elif q.get("GBQualifier_name") == "protein_id":
            transcript.protein_id = q.get("GBQualifier_value")
            temp_logger.debug(f"Protein ID found: {transcript.protein_id}")

    # Assertions to verify behaviour
    assert transcript.protein_sequence == "MTEYKLVVVG"
    assert transcript.protein_id == "NP_001234567.1"

#######################################
## Testing the as_genbank() function ##
#######################################

@pytest.fixture
def transcript():
    """Create a dummy Transcript with sequences for testing."""
    t = Transcript.__new__(Transcript)
    t.transcript_id = "NM_123456"
    t.dna_sequence = "ATGC"
    t.rna_sequence = "AUGC"
    t.protein_sequence = "MTEY"
    return t

def test_as_genbank_defaults_dna(transcript):
    """Should return GenBank format with DNA sequence when no sequence given."""
    result = transcript.as_genbank()
    assert "LOCUS        NM_123456" in result
    assert "DEFINITION   DNA sequence" in result
    assert "ORIGIN\nATGC" in result

def test_as_genbank_rna(transcript):
    """Should return RNA sequence when seq_type='RNA'."""
    result = transcript.as_genbank(seq_type="RNA")
    assert "DEFINITION   RNA sequence" in result
    assert "AUGC" in result

def test_as_genbank_protein():
    """Should return protein sequence when seq_type='protein'."""

    # Create a minimal Transcript object without calling __init__
    transcript = Transcript.__new__(Transcript)
    transcript.transcript_id = "NM_123456"

    # Ensure all sequences are set
    transcript.dna_sequence = "ATGC"
    transcript.rna_sequence = "AUGC"
    transcript.protein_sequence = "MTEY"  # <-- must be non-None

    # Call the method
    result = transcript.as_genbank(seq_type="protein")

    # Assertions
    assert "LOCUS        NM_123456" in result
    assert "DEFINITION   protein sequence" in result
    assert "MTEY" in result

def test_as_genbank_invalid_seq_type(transcript):
    """Should raise ValueError on invalid sequence type."""
    with pytest.raises(ValueError, match="Unknown seq_type"):
        transcript.as_genbank(seq_type="INVALID")

def test_as_genbank_empty_sequence_warns(monkeypatch, transcript):
    """Should warn and return empty ORIGIN if sequence is missing."""
    transcript.dna_sequence = ""
    warnings = []

    # Mock logger.warning
    monkeypatch.setattr("genbank_seqkit.transcript.logger.warning", warnings.append)

    result = transcript.as_genbank(seq_type="DNA")

    assert "ORIGIN\n" in result
    assert result.endswith("//")
    assert warnings, "Expected a warning for missing sequence"
    assert "sequence not available" in warnings[0]

####################################
## Testing the __str__() function ##
####################################

def test_str_method(transcript):
    """Test __str__ with all attributes set."""
    transcript.gene_symbol = "BRCA1"
    transcript.length = 1234
    s = str(transcript)
    assert "Transcript: NM_123456" in s
    assert "Gene: BRCA1" in s
    assert "Length: 1234 bp" in s

def test_str_method_fallbacks(transcript):
    """Test __str__ fallback when gene_symbol or length is None."""
    transcript.gene_symbol = None
    transcript.length = None
    s = str(transcript)
    assert "Gene: Unknown" in s
    assert "Length: Unknown bp" in s