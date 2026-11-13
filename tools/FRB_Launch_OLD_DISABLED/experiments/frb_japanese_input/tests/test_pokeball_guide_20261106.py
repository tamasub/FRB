from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'frb_japanese_input.py'


def test_style_uses_remote_like_green_for_kana_and_ime():
    source = MODULE.read_text(encoding='utf-8')
    assert "QPushButton#modeButton:checked {{ color: #fff; background: #416457;" in source
    assert "QPushButton#imeButton:checked {{ color: #ffffff; background: #416457;" in source
    assert "'#416457': '#d7ece1'" in source
    assert "'#86bea7': '#8fc7ab'" in source


def test_flick_guide_is_pokeball_like_not_square_overlay():
    source = MODULE.read_text(encoding='utf-8')
    assert 'self.setFixedSize(108, 108)' in source
    assert 'painter.drawEllipse(center, radius, radius)' in source
    assert 'painter.drawLine(QPointF(c - diagonal, c - diagonal),' in source
    assert 'painter.drawLine(QPointF(c - diagonal, c + diagonal),' in source
    assert 'Five-way Pokeball guide shown OUTSIDE the keyboard' in source
    assert "positions = {" in source
    assert "marker_radius" in source
