"""Temporary, opt-out telemetry for FRB ぐりぐり手裏剣 Windows diagnosis.

No GUI/Qt imports, no settings writes, and no change to wheel / flight control.
All output stays on this PC in LOCALAPPDATA/FRBLaunch/shuriken_trace.log.
Do not record filenames or the full directory path.
"""
import json
import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ===== Diagnostics ONLY: switch to False to disable the trace entirely. =====
SHURIKEN_TRACE_ENABLED = False
SHURIKEN_TRACE_MAX_BYTES = 3 * 1024 * 1024
SHURIKEN_TRACE_BACKUP_COUNT = 2
# ===========================================================================

SESSION = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}-{os.getpid()}'
MONOTONIC_START = time.monotonic()
LOGGER = None
FAILED = False


def _logger():
    global LOGGER, FAILED
    if FAILED or not SHURIKEN_TRACE_ENABLED:
        return None
    if LOGGER is None:
        try:
            root = Path(os.environ.get('LOCALAPPDATA') or str(Path.home())) / 'FRBLaunch'
            root.mkdir(parents=True, exist_ok=True)
            logger = logging.getLogger(f'frb.shuriken.trace.{os.getpid()}')
            logger.setLevel(logging.INFO)
            logger.propagate = False
            handler = RotatingFileHandler(
                root / 'shuriken_trace.log', maxBytes=SHURIKEN_TRACE_MAX_BYTES,
                backupCount=SHURIKEN_TRACE_BACKUP_COUNT, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(handler)
            LOGGER = logger
            _emit('session_start', python=os.sys.version.split()[0], pid=os.getpid())
        except Exception:
            FAILED = True
            return None
    return LOGGER


def _emit(kind, **fields):
    obj = {
        'time': datetime.now().astimezone().isoformat(timespec='milliseconds'),
        'session': SESSION,
        't_ms': round((time.monotonic() - MONOTONIC_START) * 1000, 1),
        'event': kind,
    }
    for key, value in fields.items():
        if value is None or isinstance(value, (bool, int, float, str)):
            obj[key] = value
        else:
            obj[key] = str(value)
    LOGGER.info(json.dumps(obj, ensure_ascii=False, separators=(',', ':'), default=str))


def trace(kind, **fields):
    """Best effort observation ONLY; exceptions must never affect user input."""
    if not SHURIKEN_TRACE_ENABLED:
        return
    try:
        if _logger() is not None:
            _emit(kind, **fields)
    except Exception:
        pass


def bar_state(bar, *, row_count=None):
    """Lightweight numeric-only scrollbar snapshot for event logs."""
    if bar is None:
        return {'bar': 'none', 'rows': row_count}
    try:
        return {'pos': bar.value(), 'minimum': bar.minimum(), 'maximum': bar.maximum(),
                'page_step': bar.pageStep(), 'single_step': bar.singleStep(),
                'rows': row_count}
    except Exception:
        return {'bar': 'invalid', 'rows': row_count}
