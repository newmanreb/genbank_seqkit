# src/tests/test__force_list.py
import pytest
import importlib

force_list_mod = importlib.import_module("genbank_seqkit.utils._force_list")


def test_force_list_with_none(monkeypatch):
    class DummyLogger:
        def __init__(self):
            self.logged = False
        def debug(self, msg):
            self.logged = True

    dummy_logger = DummyLogger()
    monkeypatch.setattr(force_list_mod, "logger", dummy_logger)

    result = force_list_mod._force_list(None, verbose=True)
    assert result == []
    assert dummy_logger.logged


def test_force_list_with_existing_list(monkeypatch):
    class DummyLogger:
        def __init__(self):
            self.msg = None
        def debug(self, msg):
            self.msg = msg

    dummy_logger = DummyLogger()
    monkeypatch.setattr(force_list_mod, "logger", dummy_logger)

    lst = [1, 2, 3]
    result = force_list_mod._force_list(lst, verbose=True)
    assert result is lst
    assert "length 3" in dummy_logger.msg


def test_force_list_with_scalar(monkeypatch):
    class DummyLogger:
        def __init__(self):
            self.msg = None
        def debug(self, msg):
            self.msg = msg

    dummy_logger = DummyLogger()
    monkeypatch.setattr(force_list_mod, "logger", dummy_logger)

    result = force_list_mod._force_list("x", verbose=True)
    assert result == ["x"]
    assert "single item" in dummy_logger.msg


def test_force_list_without_verbose(monkeypatch):
    class DummyLogger:
        def debug(self, msg):
            pytest.fail("Logger.debug should not be called when verbose=False")

    dummy_logger = DummyLogger()
    monkeypatch.setattr(force_list_mod, "logger", dummy_logger)

    result = force_list_mod._force_list("x", verbose=False)
    assert result == ["x"]