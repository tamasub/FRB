"""Temporary privacy-minimal first-hand gesture diagnostics.

Events contain only elapsed time, mouse deltas, slot index and event labels.
No file paths, item titles, commands or JSON content are recorded. Log output:
%LOCALAPPDATA%/FRBLaunch/first_hand_trace.log (max 256 KiB + 1 rotation).
"""
import json
import logging
import os
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler

FIRST_HAND_TRACE_ENABLED = True  # Turn off after Windows diagnosis.
_log = None
_failed = False
_start = time.monotonic()


def first_hand_trace(event, **fields):
    global _log, _failed
    if not FIRST_HAND_TRACE_ENABLED or _failed:
        return
    try:
        if _log is None:
            path = Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'FRBLaunch'
            path.mkdir(parents=True, exist_ok=True)
            logger = logging.getLogger('frb.launch.first_hand')
            logger.setLevel(logging.INFO)
            logger.propagate = False
            if not logger.handlers:
                handle = RotatingFileHandler(path / 'first_hand_trace.log',
                                             maxBytes=262144, backupCount=1,
                                             encoding='utf-8')
                handle.setFormatter(logging.Formatter('%(message)s'))
                logger.addHandler(handle)
            _log = logger
        record = {'event': str(event),
                  'elapsed_ms': round((time.monotonic() - _start) * 1000, 1)}
        for key, value in fields.items():
            if isinstance(value, (bool, int, float)):
                record[key] = value
            elif key == 'reason':
                record['reason'] = str(value)[:64]
        _log.info(json.dumps(record, ensure_ascii=False))
    except Exception:
        _failed = True  # Logging must never affect mouse/Launch behavior.
