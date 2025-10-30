# src/tests/test_entrez_efetch.py
import pytest
import importlib

# Import the module dynamically
efetch_mod = importlib.import_module("genbank_seqkit.utils.entrez_efetch")
errors_mod = importlib.import_module("genbank_seqkit.errors")

# Dummy record for mocking
dummy_record = {"GBSeq_locus": "NM_000093"}

# -----------------------------
# Test: Successful fetch
# -----------------------------
def test_fetch_transcript_record_success(monkeypatch):
    """Test that a valid transcript ID returns a parsed record."""

    # Mock requests.get
    class DummyResponse:
        text = "<GBSet><GBSeq><GBSeq_locus>NM_000093</GBSeq_locus></GBSeq></GBSet>"

        def raise_for_status(self):
            return None  # No exception

    monkeypatch.setattr(efetch_mod.requests, "get", lambda url, params, timeout: DummyResponse())
    # Mock xmltodict.parse
    monkeypatch.setattr(efetch_mod.xmltodict, "parse", lambda text: {"GBSet": {"GBSeq": dummy_record}})

    result = efetch_mod.fetch_transcript_record("NM_000093.5")
    assert result == dummy_record


# -----------------------------
# Test: Invalid transcript ID
# -----------------------------
@pytest.mark.parametrize("invalid_id", ["AB_000093.5", "NM_000093", "12345"])
def test_fetch_transcript_record_invalid_id(invalid_id):
    """Test that invalid transcript IDs raise TranscriptIdError."""
    with pytest.raises(errors_mod.TranscriptIdError):
        efetch_mod.fetch_transcript_record(invalid_id)


# -----------------------------
# Test: XML parsing error
# -----------------------------
def test_fetch_transcript_record_parse_error(monkeypatch):
    """Test that XML parsing errors raise GenbankParseError."""
    class DummyResponse:
        text = "<invalid></xml>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(efetch_mod.requests, "get", lambda url, params, timeout: DummyResponse())
    # Force xmltodict.parse to raise
    def raise_parse(text):
        raise ValueError("XML invalid")

    monkeypatch.setattr(efetch_mod.xmltodict, "parse", raise_parse)

    with pytest.raises(errors_mod.GenbankParseError):
        efetch_mod.fetch_transcript_record("NM_000093.5")


# -----------------------------
# Test: Network error
# -----------------------------
def test_fetch_transcript_record_network_error(monkeypatch):
    """Test that network errors raise GenbankFetchError."""
    import requests

    def raise_request(*args, **kwargs):
        raise requests.exceptions.RequestException("Network problem")

    monkeypatch.setattr(efetch_mod.requests, "get", raise_request)

    with pytest.raises(errors_mod.GenbankFetchError):
        efetch_mod.fetch_transcript_record("NM_000093.5")