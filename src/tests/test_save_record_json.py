# src/tests/test_save_record_json.py
import json
from pathlib import Path
import pytest
import importlib

# Import the module (not the function) for monkeypatching
save_mod = importlib.import_module("genbank_seqkit.utils.save_record_json")

dummy_record = {"GBSeq_accession-version": "NM_000093.5", "GBSeq_sequence": "ATGCGT"}

def test_save_record_json_default(tmp_path, monkeypatch):
    """Test saving record with default filename and directory."""
    monkeypatch.setattr(save_mod, "fetch_transcript_record", lambda tid: dummy_record)

    # Patch data_dir to use tmp_path
    result_path = save_mod.save_record_json("NM_000093.5", data_dir=tmp_path)
    assert result_path.exists()
    with open(result_path) as f:
        data = json.load(f)
    assert data == dummy_record

def test_save_record_json_custom_filename(tmp_path, monkeypatch):
    """Test saving record with a custom filename."""
    monkeypatch.setattr(save_mod, "fetch_transcript_record", lambda tid: dummy_record)

    custom_file = tmp_path / "custom.json"
    result_path = save_mod.save_record_json("NM_000093.5", filename=custom_file)
    assert result_path == custom_file
    with open(result_path) as f:
        data = json.load(f)
    assert data == dummy_record

def test_save_record_json_pretty_print(tmp_path, monkeypatch, capsys):
    """Test pretty_print option prints to console."""
    monkeypatch.setattr(save_mod, "fetch_transcript_record", lambda tid: dummy_record)

    save_mod.save_record_json("NM_000093.5", data_dir=tmp_path, pretty_print=True)
    captured = capsys.readouterr()
    assert "GBSeq_accession-version" in captured.out

def test_save_record_json_unexpected_error(tmp_path, monkeypatch):
    """Test that an unexpected exception raises GenbankError."""
    def raise_error(tid):
        raise RuntimeError("oops")

    monkeypatch.setattr(save_mod, "fetch_transcript_record", raise_error)

    with pytest.raises(save_mod.GenbankError):
        save_mod.save_record_json("NM_000093.5", data_dir=tmp_path)