"""Observational-only contract for the temporary Windows shuriken trace."""
import json
import importlib
from pathlib import Path


def test_trace_writes_jsonl_to_separate_frb_directory(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    import shuriken_trace as mod
    mod = importlib.reload(mod)
    mod.trace('diagnostic_check', steps=-1, rows=4700, pos=123)
    destination = tmp_path / 'FRBLaunch' / 'shuriken_trace.log'
    assert destination.is_file()
    rows = [json.loads(line) for line in destination.read_text(encoding='utf-8').splitlines()]
    assert rows[0]['event'] == 'session_start'
    assert rows[-1]['event'] == 'diagnostic_check'
    assert rows[-1]['steps'] == -1
    assert rows[-1]['rows'] == 4700
    assert rows[-1]['pos'] == 123
    assert all('session' in row and 't_ms' in row for row in rows)
    for handler in mod.LOGGER.handlers:
        handler.close()
        mod.LOGGER.removeHandler(handler)
    mod.LOGGER = None


def test_disabled_trace_never_creates_log(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    import shuriken_trace as mod
    mod = importlib.reload(mod)
    monkeypatch.setattr(mod, 'SHURIKEN_TRACE_ENABLED', False)
    mod.trace('should_not_write', pos=100)
    assert not (tmp_path / 'FRBLaunch' / 'shuriken_trace.log').exists()


def test_gate_decisions_unchanged_when_diagnostics_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    import shuriken_trace as mod
    import guriguri_shuriken_auto as gate_mod
    gate_mod = importlib.reload(gate_mod)
    # The test drives the exact same now / steps / source sequence both ways.
    samples = [(0, 1), (0.08, 1), (0.16, 1), (0.24, 1),
               (0.32, 1), (0.40, 1), (0.48, 1), (0.9, -1)]
    def run(enabled):
        monkeypatch.setattr(mod, 'SHURIKEN_TRACE_ENABLED', enabled)
        gate = gate_mod.WheelShurikenGate()
        return [gate.feed(steps, now=now, source='list') for now, steps in samples]
    assert run(False) == run(True)


def test_source_contains_no_user_path_logging():
    # Do not collect file names, URLs, directories, or clipboard contents.
    src = (Path(__file__).resolve().parents[1] / 'src' / 'shuriken_trace.py').read_text(encoding='utf-8')
    assert 'file_name=' not in src
    assert 'current_directory=' not in src
