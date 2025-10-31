import pytest
from genbank_seqkit.transcript import Transcript
from genbank_seqkit.errors import GenbankError, TranscriptIdError, GenbankFetchError, GenbankParseError
from unittest.mock import patch

# Test that a Transcript object instantiates correctly
@patch("genbank_seqkit.transcript.Transcript._fetch_and_populate")
def test_transcript_init(mock_fetch):
    t = Transcript("NM_000093.5")
    mock_fetch.assert_called_once()
    assert t.transcript_id == "NM_000093.5"
    assert t.gene_symbol is None
    assert t.dna_sequence is None

#################################################
## Testing the _fetch_and_populate() function ##
#################################################

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

# Test for parsing for protein sequence and id assignment
@patch('genbank_seqkit.transcript.fetch_transcript_record')
def test_cds_and_protein_info_coverage(mock_fetch):
    """Covers the CDS feature parsing and protein_sequence / protein_id assignment."""
    mock_fetch.return_value = {
        'GBSeq_accession-version': 'NM_123456',
        'GBSeq_sequence': 'ATGCGT',
        'GBSeq_feature-table': {
            'GBFeature': [
                {
                    'GBFeature_key': 'CDS',
                    'GBFeature_quals': {
                        'GBQualifier': [
                            {'GBQualifier_name': 'translation', 'GBQualifier_value': 'MTEYK'},
                            {'GBQualifier_name': 'protein_id', 'GBQualifier_value': 'NP_123456.1'}
                        ]
                    }
                }
            ]
        }
    }

    transcript = Transcript("NM_123456")

    assert transcript.protein_sequence == "MTEYK"
    assert transcript.protein_id == "NP_123456.1"
    assert transcript.dna_sequence == "ATGCGT"
    assert transcript.length is None  # still fine since mock record omits GBSeq_length

# Test for warnings for missing attributes in _fetch_and_populate
@patch("genbank_seqkit.transcript.fetch_transcript_record")
def test_missing_attributes_logging(mock_fetch, caplog):
    """Covers missing gene_symbol, hgnc_id, protein_sequence, and protein_id warnings."""
    # Return a minimal record missing those fields
    mock_fetch.return_value = {
        "GBSeq_accession-version": "NM_999999",
        "GBSeq_sequence": "ATGCGT",
        "GBSeq_feature-table": {"GBFeature": []}
    }

    with caplog.at_level("WARNING"):
        t = Transcript("NM_999999")

    # Ensure all expected warnings are present
    warnings = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("No gene symbol found" in w for w in warnings)
    assert any("No hgnc ID found" in w for w in warnings)
    assert any("No protein sequence found" in w for w in warnings)
    assert any("Protein ID missing" in w for w in warnings)

    # Confirm that the transcript initialized successfully
    assert t.transcript_id == "NM_999999"
    assert t.dna_sequence == "ATGCGT"
    assert t.rna_sequence == "AUGCGU"

# Test custom exception handling in _fetch_and_populate
@patch("genbank_seqkit.transcript.fetch_transcript_record", side_effect=TranscriptIdError("bad ID"))
def test_transcript_id_error(mock_fetch):
    """Covers the TranscriptIdError branch."""
    with pytest.raises(TranscriptIdError):
        Transcript("NM_BADID")

@patch("genbank_seqkit.transcript.fetch_transcript_record", side_effect=GenbankFetchError("fetch failed"))
def test_genbank_fetch_error(mock_fetch):
    """Covers the GenbankFetchError branch."""
    with pytest.raises(GenbankFetchError):
        Transcript("NM_FETCHFAIL")

@patch("genbank_seqkit.transcript.fetch_transcript_record", side_effect=GenbankParseError("parse failed"))
def test_genbank_parse_error(mock_fetch):
    """Covers the GenbankParseError branch."""
    with pytest.raises(GenbankParseError):
        Transcript("NM_PARSEFAIL")

@patch("genbank_seqkit.transcript.fetch_transcript_record", side_effect=Exception("unexpected failure"))
def test_generic_exception_branch(mock_fetch):
    """Covers the generic Exception -> GenbankError branch."""
    with pytest.raises(GenbankError):
        Transcript("NM_GENERIC")

# Test to cover TranscriptIdError in _fetch_and_populate
def test_transcriptid_error_handling(caplog):
    """Cover TranscriptIdError in _fetch_and_populate."""
    from genbank_seqkit.errors import TranscriptIdError

    with patch('genbank_seqkit.transcript.fetch_transcript_record', side_effect=TranscriptIdError("bad ID")):
        transcript = Transcript.__new__(Transcript)
        transcript.transcript_id = "BAD_ID"
        with caplog.at_level("ERROR"):
            with pytest.raises(TranscriptIdError):
                transcript._fetch_and_populate(verbose=True)
        assert any("Error processing transcript" in m for m in [rec.message for rec in caplog.records])


######################################
## Testing the as_fasta() function ##
######################################

# Test FASTA format without API calling
def test_as_fasta_returns_expected_format():
    t = Transcript.__new__(Transcript)  # bypass __init__ to skip fetching
    t.transcript_id = "NM_000093.5"
    t.dna_sequence = "ATGC"
    fasta = t.as_fasta(seq_type="DNA")
    assert fasta.startswith(">NM_000093.5 | DNA")
    assert "ATGC" in fasta

# Test error handling in as_fasta()
def test_as_fasta_raises_for_unknown_type():
    t = Transcript.__new__(Transcript)
    t.transcript_id = "NM_000093.5"
    with pytest.raises(ValueError):
        t.as_fasta(seq_type="invalid")

#######################################
## Testing the as_genbank() function ##
#######################################

# Test GenBank formatting without API calling
def test_as_genbank_contains_locus_and_origin():
    t = Transcript.__new__(Transcript)
    t.transcript_id = "NM_000093.5"
    t.dna_sequence = "ATGC"
    gb = t.as_genbank(seq_type="DNA")
    assert "LOCUS" in gb
    assert "ORIGIN" in gb

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