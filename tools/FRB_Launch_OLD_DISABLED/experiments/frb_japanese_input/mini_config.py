"""GUI-independent size/gesture presets for FRB Japanese Input mini."""

from dataclasses import dataclass

@dataclass(frozen=True)
class MiniSize:
    name: str
    outer_width: int
    outer_height: int
    key_height: int
    font_size: int
    guide_size: int
    threshold: int


# Outer dimensions include Windows' title bar when Qt reports frame geometry.
# The preset can be selected at run time without restarting the app.
SIZE_PRESETS = (
    MiniSize("最小", 174, 252, 25, 17, 68, 8),
    MiniSize("小",   186, 262, 28, 18, 74, 9),
    MiniSize("Remote", 200, 272, 31, 20, 80, 10),
    MiniSize("大",   222, 296, 36, 22, 90, 12),
)
DEFAULT_SIZE_INDEX = 2
THRESHOLD_OPTIONS = (7, 8, 9, 10, 12, 14, 18)


def compact_client_height(size: MiniSize, frame_height: int) -> int:
    """Client height for the native-IME editor at the bottom; no empty candidate spacer."""
    return max(195, size.outer_height - frame_height)
