"""Regression contracts for moving Kana Delete/Clear above IME candidates."""
from __future__ import annotations

import ast
from pathlib import Path

KANA = Path(__file__).resolve().parents[1] / 'experiments/frb_japanese_input/frb_japanese_input.py'
SOURCE = KANA.read_text(encoding='utf-8')


def _build_ui_body() -> str:
    # No Qt dependency: inspect the actual method, not comments or other methods.
    module = ast.parse(SOURCE)
    window = next(node for node in module.body if isinstance(node, ast.ClassDef)
                  and node.name == 'MiniJapaneseInputWindow')
    method = next(node for node in window.body if isinstance(node, ast.FunctionDef)
                  and node.name == '_build_ui')
    return ast.get_source_segment(SOURCE, method)


def test_delete_and_clear_are_top_left_above_the_mode_strip_and_keyboard():
    body = _build_ui_body()
    assert body.count('self.del_button = self._micro(') == 1
    assert body.count('self.clear_button = self._micro(') == 1
    assert body.index('top.addWidget(self.del_button)') < body.index('top.addWidget(self.clear_button)')
    assert body.index('top.addWidget(self.clear_button)') < body.index('top.addStretch(1)')
    assert body.index('top.addWidget(self.clear_button)') < body.index('root.addLayout(top)')
    assert body.index('root.addLayout(top)') < body.index('root.addLayout(mode_strip)')
    assert body.index('root.addLayout(mode_strip)') < body.index('root.addWidget(keyboard)')


def test_delete_and_clear_are_not_duplicated_at_bottom():
    body = _build_ui_body()
    assert 'actions.addWidget(self.del_button)' not in body
    assert 'actions.addWidget(self.clear_button)' not in body
    for remaining in ('enter_button', 'copy_button', 'send_button'):
        assert f'actions.addWidget(self.{remaining})' in body
    assert "self.del_button.setToolTip(\"末尾の文字を削除\")" in body
    assert 'self._micro("", self._backspace, 27, \'kanaDeleteButton\')' in body
    assert 'self.del_button.setIconSize(QSize(22, 16))' in body
    assert 'self._micro("全消", self._clear, 30)' in body


def test_drawn_delete_icon_and_both_themes():
    module = ast.parse(SOURCE)
    style = next(node for node in module.body if isinstance(node, ast.FunctionDef)
                 and node.name == 'style_for_size')
    namespace = {}
    exec(compile(ast.Module(body=[style], type_ignores=[]), str(KANA), 'exec'), namespace)
    for theme in ('dark', 'light'):
        css = namespace['style_for_size'](20, theme)
        assert 'QPushButton#kanaDeleteButton {' in css
        delete_style = css.split('QPushButton#kanaDeleteButton {', 1)[1].split('}', 1)[0]
        assert 'font-size:' not in delete_style
        assert 'padding: 0;' in delete_style
        assert 'QPushButton#kanaDeleteButton:hover {' in css


def test_no_change_to_native_ime_editor_position():
    body = _build_ui_body()
    assert body.index('root.addLayout(actions)') < body.index('self.output = NativeImeLineEdit(self)')
    assert body.index('self.output = NativeImeLineEdit(self)') < body.index('root.addWidget(self.output)')
    assert 'self.enter_button = self._micro("確定↵", self._commit' in body
    assert 'self.send_button = self._micro("送信", self._request_send' in body


def test_delete_is_a_drawn_icon_not_a_font_glyph():
    module = ast.parse(SOURCE)
    helper = next(node for node in module.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'backspace_button_icon')
    implementation = ast.get_source_segment(SOURCE, helper)
    assert 'QPainterPath()' in implementation
    assert 'painter.drawPath(outline)' in implementation
    assert implementation.count('painter.drawLine(') == 2
    assert "'#454545' if light else '#9bb9aa'" in implementation
    assert "'#ffffff' if light else '#263b31'" in implementation
    assert 'image.setDevicePixelRatio(scale)' in implementation
    assert 'self.del_button.setIcon(backspace_button_icon(light))' in SOURCE
    assert 'self.del_button.setText("⌫")' not in SOURCE
