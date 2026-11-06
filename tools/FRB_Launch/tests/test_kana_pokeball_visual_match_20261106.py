"""Ensure the kana guide keeps the quieter FRB Shuriken outline and eye."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KANA = (ROOT / 'experiments/frb_japanese_input/frb_japanese_input.py').read_text('utf-8')
SHURIKEN = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')


def test_kana_circle_fill_and_outline_match_shuriken():
    assert 'painter.setBrush(QColor(228, 244, 215, 255))' in SHURIKEN
    assert 'painter.setPen(QPen(QColor(154, 196, 119, 210), 1.2))' in SHURIKEN
    assert 'background = QColor(228, 244, 215, 255)' in KANA
    assert 'border = QColor(154, 196, 119, 210)' in KANA
    assert 'painter.setPen(QPen(border, 1.2))' in KANA


def test_kana_eye_and_dividers_match_shuriken():
    assert 'painter.setPen(QPen(QColor(159, 195, 133, 185), 1.0))' in SHURIKEN
    assert 'divider = QColor(159, 195, 133, 185)' in KANA
    assert 'painter.setPen(QPen(divider, 1.0))' in KANA
    assert "painter.setPen(QPen(QColor('#385e56'), 1.2))" in KANA
    assert "painter.setPen(QPen(QColor('#426d59'), 1.0))" in SHURIKEN
    assert "painter.setBrush(QColor('#aed2a0'))" in SHURIKEN
    assert "painter.setPen(QPen(QColor('#426d59'), 1.0))" in KANA
    assert "painter.setBrush(QColor('#aed2a0'))" in KANA


def test_gesture_handoff_untouched():
    # This change is visual only: marker direction still comes from the key.
    assert 'chosen = self.direction' in KANA
    assert 'if chosen in positions and flick_hint(self.kana_name, chosen) is not None:' in KANA
    assert 'self.gesture_finished.emit(self.kana_name, direction)' in KANA
