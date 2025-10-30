# src/tests/test_save_record_json.py
import pytest
import json
from pathlib import Path
import importlib

# Dynamically import the module so monkeypatching works reliably
save_mod = importlib.import_module("genbank_seqkit.utils.save_record_json")
from genbank_seqkit.errors import GenbankError

dummy_record = {"GBSeq_accession-version": "NM_000093.4"}

def test_save_record_json_default(tmp_path, monkeypatch):
    """Test saving record with default filename and directory."""
    monkeypatch.setattr(save_mod, "fetch_transcript_record", lambda tid: dummy_record)

    out_file = save_mod.save_record_json("NM_000093.4", data_dir=tmp_path)
    assert out_file.exists()
    with open(out_file) as f:
        data = json.load(f)
    assert data == dummy_record

def test_save_record_json_custom_filename(tmp_path, monkeypatch):
    """Test saving record with a custom filename."""
    monkeypatch.setattr(save_mod, "fetch_transcript_record", lambda tid: dummy_record)
    custom_file = tmp_path / "myfile.json"
    out_file = save_mod.save_record_json("NM_000093.4", filename=custom_file)
    assert out_file.exists()
    assert out_file.name == "myfile.json"

def test_save_record_json_pretty_print(tmp_path, monkeypatch, capsys):
    """Test pretty_print option prints to console."""
    monkeypatch.setattr(save_mod, "fetch_transcript_record", lambda tid: dummy_record)
    save_mod.save_record_json("NM_000093.4", data_dir=tmp_path, pretty_print=True)
    captured = capsys.readouterr()
    assert "GBSeq_accession-version" in captured.out

def test_save_record_json_unexpected_error(monkeypatch, tmp_path):
    """Test that an unexpected exception raises GenbankError."""
    def raise_error(tid):
        raise RuntimeError("oops")
    monkeypatch.setattr(save_mod, "fetch_transcript_record", raise_error)
    with pytest.raises(GenbankError):
        save_mod.save_record_json("NM_000093.4", data_dir=tmp_path)