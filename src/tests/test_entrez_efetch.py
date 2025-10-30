import pytest
import types
from genbank_seqkit.utils import entrez_efetch as entrez_mod

def test_invalid_transcript_id_prefix():
    """Transcript ID must start with NM_, NR_, XM_, XR_"""
    with pytest.raises(entrez_mod.TranscriptIdError):
        entrez_mod.fetch_transcript_record("AB_123456.1")

def test_missing_version_number():
    """Transcript ID must include a version number"""
    with pytest.raises(entrez_mod.TranscriptIdError):
        entrez_mod.fetch_transcript_record("NM_123456")

def test_network_error(monkeypatch):
    """Simulate network failure"""

    class DummyRequests:
        class exceptions:
            RequestException = Exception
        def get(self, url, params, timeout):
            raise self.exceptions.RequestException("network down")

    monkeypatch.setattr(entrez_mod, "requests", DummyRequests())

    with pytest.raises(entrez_mod.GenbankFetchError):
        entrez_mod.fetch_transcript_record("NM_000093.4")

def test_xml_parse_error(monkeypatch):
    """Simulate invalid XML returned"""

    class DummyResponse:
        text = "<invalid><xml>"

        def raise_for_status(self):
            pass

    class DummyRequests:
        class exceptions:
            RequestException = Exception
        def get(self, url, params, timeout):
            return DummyResponse()

    class DummyXmltodict:
        @staticmethod
        def parse(text):
            raise ValueError("bad xml")

    monkeypatch.setattr(entrez_mod, "requests", DummyRequests())
    monkeypatch.setattr(entrez_mod, "xmltodict", DummyXmltodict())

    with pytest.raises(entrez_mod.GenbankParseError):
        entrez_mod.fetch_transcript_record("NM_000093.4")

def test_successful_fetch(monkeypatch):
    """Valid transcript fetch returns expected dict"""

    dummy_record = {"GBSeq_accession-version": "NM_000093.4"}

    class DummyResponse:
        text = "<xml>dummy</xml>"

        def raise_for_status(self):
            pass

    class DummyRequests:
        class exceptions:
            RequestException = Exception
        def get(self, url, params, timeout):
            return DummyResponse()

    class DummyXmltodict:
        @staticmethod
        def parse(text):
            return {"GBSet": {"GBSeq": dummy_record}}

    monkeypatch.setattr(entrez_mod, "requests", DummyRequests())
    monkeypatch.setattr(entrez_mod, "xmltodict", DummyXmltodict())

    result = entrez_mod.fetch_transcript_record("NM_000093.4")
    assert result == dummy_record