"""FRB Remote right-click proof-of-concept wiring regression checks."""
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'


def test_wheel_pad_emits_separate_context_command():
    source = (SRC / 'launch_remote.py').read_text(encoding='utf-8')
    assert "event.button() == Qt.MouseButton.RightButton" in source
    assert "self.command.emit('CONTEXT_MENU')" in source
    assert "self.command.emit('CLICK')" in source
    assert "self.command.emit('DOUBLE_CLICK')" in source


def test_remote_routes_to_existing_context_menu():
    source = (SRC / 'app.py').read_text(encoding='utf-8')
    assert "if command == 'CONTEXT_MENU':" in source
    method = source.split('    def remote_context_menu(self):', 1)[1].split('    def remote_command(', 1)[0]
    assert 'show_launch_context_menu(pos, row' in method
    assert 'view.context_menu(pane, rect.center(), global_pos=pos)' in method
    assert 'self.show_expanded_background_paste_menu(pos)' in method
    assert 'pad.mapToGlobal(' in method
    assert 'QCursor.setPos' not in method


def test_expanded_context_menu_keeps_existing_actions_and_rename():
    source = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
    method = source.split('    def context_menu(self, pane, point, *, global_pos=None):', 1)[1].split('    def ', 1)[0]
    assert 'selected_paths=targets' in method
    assert 'begin_context_inline_rename' in method
    assert 'global_pos if global_pos is not None' in method
