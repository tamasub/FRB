"""Resolve the small FRB Remote shuriken icon in source and PyInstaller builds."""
from pathlib import Path
import sys


def resource_root(source_file):
    """Bundled data are beneath sys._MEIPASS, not necessarily __file__/../.."""
    frozen_root = getattr(sys, '_MEIPASS', None)
    return Path(frozen_root) if frozen_root else Path(source_file).resolve().parent.parent
