# src/tests/test_entrez_efetch.py
import pytest
import importlib

# Import the module via importlib to ensure coverage is tracked
efetch_mod = importlib.import_module("genbank_seqkit.utils.entrez_efetch")
errors_mod = importlib.import_module("genbank_seqkit.errors")

dummy_record = {"GBSeq_accession-version": "NM_000093.5", "GBSeq_sequence": "ATGCGT"}

def test_fetch_transcript_record_success(monkeypatch):
    """Test that a valid transcript ID returns a parsed record."""

    class DummyResponse:
        text = "<GBSet><GBSeq><GBSeq_locus>NM_000093</GBSeq_locus></GBSeq></GBSet>"
        def raise_for_status(self):
            return None

    monkeypatch.setattr(efetch_mod.requests, "get", lambda url, params, timeout: DummyResponse())
    monkeypatch.setattr(efetch_mod.xmltodict, "parse", lambda text: {"GBSet": {"GBSeq": dummy_record}})

    result = efetch_mod.fetch_transcript_record("NM_000093.5")
    assert result == dummy_record

def test_fetch_transcript_record_invalid_prefix():
    """Test that invalid transcript IDs raise TranscriptIdError."""
    with pytest.raises(errors_mod.TranscriptIdError):
        efetch_mod.fetch_transcript_record("AB_000093.5")

def test_fetch_transcript_record_missing_version():
    """Test that transcript IDs without version raise TranscriptIdError."""
    with pytest.raises(errors_mod.TranscriptIdError):
        efetch_mod.fetch_transcript_record("NM_000093")

def test_fetch_transcript_record_network_error(monkeypatch):
    """Test that network errors raise GenbankFetchError."""

    def raise_request(*args, **kwargs):
        raise efetch_mod.requests.exceptions.RequestException("Network problem")

    monkeypatch.setattr(efetch_mod.requests, "get", raise_request)
    with pytest.raises(errors_mod.GenbankFetchError):
        efetch_mod.fetch_transcript_record("NM_000093.5")

def test_fetch_transcript_record_parse_error(monkeypatch):
    """Test that parse errors raise GenbankParseError."""

    class DummyResponse:
        text = "invalid xml"
        def raise_for_status(self):
            return None

    monkeypatch.setattr(efetch_mod.requests, "get", lambda url, params, timeout: DummyResponse())
    monkeypatch.setattr(efetch_mod.xmltodict, "parse", lambda text: (_ for _ in ()).throw(Exception("bad xml")))

    with pytest.raises(errors_mod.GenbankParseError):
        efetch_mod.fetch_transcript_record("NM_000093.5")