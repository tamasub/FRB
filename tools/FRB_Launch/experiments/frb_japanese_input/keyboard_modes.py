"""Pure definitions for FRB kana/English/symbol/numeric virtual key layouts.

The kana 3x4 flick layout remains in frb_kana_core; these modes use direct
insertion into the editor, so they never create an IME preedit session.
"""
from __future__ import annotations
from dataclasses import dataclass

MODES = ('kana', 'latin', 'symbols', 'numeric')
MODE_LABELS = {'kana':'かな', 'latin':'ABC', 'symbols':'記号', 'numeric':'数字'}
MODE_COLUMNS = {'latin':10, 'symbols':10, 'numeric':5}

@dataclass(frozen=True)
class KeyDef:
    row: int
    col: int
    label: str
    text: str = ''
    action: str = 'insert'
    span: int = 1


def _row(row: int, labels: str, start: int = 0) -> list[KeyDef]:
    return [KeyDef(row, start + col, ch, ch) for col, ch in enumerate(labels)]


def layout_for(mode: str) -> tuple[KeyDef, ...]:
    """Grid coordinates plus user-facing actions, free of Qt and WinAPI."""
    if mode == 'latin':
        result = _row(0, 'qwertyuiop')
        result += [KeyDef(1, 0, '', action='spacer')]
        result += _row(1, 'asdfghjkl', 1)
        result += [KeyDef(2, 0, '⇧', action='shift')]
        result += _row(2, 'zxcvbnm', 1)
        result += [KeyDef(2, 8, '⌫', action='backspace')]
        result += [KeyDef(2, 9, '↵', action='enter')]
        result += [KeyDef(3, 0, ',', ','), KeyDef(3, 1, '?', '?'),
                   KeyDef(3, 2, '空白', ' ', span=6),
                   KeyDef(3, 8, '.', '.'), KeyDef(3, 9, '@', '@')]
        return tuple(result)
    if mode == 'symbols':
        result = _row(0, '1234567890')
        result += _row(1, '@#¥%&-+()/')
        result += _row(2, "*\"':;!?、.")  # 9 characters, then backspace
        result += [KeyDef(2, 9, '⌫', action='backspace')]
        result += [KeyDef(3, 0, '\\', '\\'), KeyDef(3, 1, '=', '='),
                   KeyDef(3, 2, '空白', ' ', span=6),
                   KeyDef(3, 8, '…', '…'), KeyDef(3, 9, '↵', action='enter')]
        return tuple(result)
    if mode == 'numeric':
        rows = (
            [('+', '+'), ('1', '1'), ('2', '2'), ('3', '3'), ('%', '%')],
            [('-', '-'), ('4', '4'), ('5', '5'), ('6', '6'), ('⌫', None)],
            [('*', '*'), ('7', '7'), ('8', '8'), ('9', '9'), ('↵', None)],
            [('/', '/'), (',', ','), ('0', '0'), ('.', '.'), ('=', '=')],
        )
        return tuple(KeyDef(r, c, label, text or '',
                            'backspace' if label == '⌫' else 'enter' if label == '↵' else 'insert')
                     for r, row in enumerate(rows) for c, (label, text) in enumerate(row))
    raise ValueError(f'Unsupported keyboard mode: {mode}')


def validate_layout(mode: str) -> bool:
    columns = MODE_COLUMNS[mode]
    occupied = set()
    for key in layout_for(mode):
        if key.row < 0 or key.col < 0 or key.span < 1 or key.col + key.span > columns:
            return False
        for col in range(key.col, key.col + key.span):
            if (key.row, col) in occupied:
                return False
            occupied.add((key.row, col))
    return all((row, col) in occupied for row in range(4) for col in range(columns))


def ime_key_for(mode: str) -> str:
    """Use Microsoft Japanese IME's explicit ImeOn/ImeOff virtual keys."""
    if mode not in MODES:
        raise ValueError(f'Unsupported keyboard mode: {mode}')
    return 'IME_ON' if mode == 'kana' else 'IME_OFF'


def request_ime_mode(mode: str, sender, check_focus) -> None:
    """Send the mode key only when the FRB editor is the actual target."""
    key = ime_key_for(mode)
    if not check_focus():
        raise RuntimeError('入力欄にフォーカスがありません')
    sender.send_tokens([key])
