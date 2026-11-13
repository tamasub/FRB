"""Checks for in-address favorite controls, popup geometry, and deferred drag."""
import ast
from pathlib import Path
from types import SimpleNamespace

SRC = Path(__file__).resolve().parents[1] / 'src'
VIEW = (SRC / 'expanded_view.py').read_text('utf-8')
TREE = (SRC / 'reorderable_tree.py').read_text('utf-8')


def test_favorite_controls_inside_round_address_field():
    ast.parse(VIEW)
    assert 'self.favorite_save = QToolButton(self.address_bar)' in VIEW
    assert 'self.address_bar.attach_favorite_save(self.favorite_save)' in VIEW
    assert 'shared_layout.addWidget(self.favorite_save)' not in VIEW
    assert 'self.crumb_layout.setContentsMargins(4, 1, 64, 1)' in VIEW
    assert 'self.editor.setTextMargins(0, 0, 60, 0)' in VIEW
    assert 'border-radius:17px' in VIEW
    assert "self.favorite_save.setText('🩶' if registered else '💛')" in VIEW


def test_popup_matches_input_width_and_content_not_twice_the_history_height():
    start = VIEW.index('    def position_directory_favorites(self):')
    end = VIEW.index('    def toggle_directory_favorites(self):', start)
    code = VIEW[start:end]
    assert 'self.address_bar.mapTo(self.launcher' in code
    assert 'width = min(self.address_bar.width()' in code
    assert 'popup_available_height(' in code
    assert 'popup_tree_height(' in code
    assert 'footer_top = self.launcher.footer.mapTo(' in code
    assert '* 2' not in code
    assert 'self.favorite_popup.setGeometry(x, y, width, height)' in code


def test_drag_defers_mutation_until_after_qt_move_cleanup():
    """Exercise the drag-event algorithm without Windows/PySide6 dependencies."""
    module = ast.parse(TREE)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef))
    funcs = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    scheduled = []
    ns = {'Qt': SimpleNamespace(), 'QTimer': SimpleNamespace(singleShot=lambda ms, cb: scheduled.append(cb))}
    exec(compile(ast.Module(body=[funcs['dropEvent'], funcs['_finish_root_reorder']], type_ignores=[]),
                 '<reorderable_tree>', 'exec'), ns)

    class Item:
        def __init__(self, value): self.value = value

    class Tree:
        def __init__(self):
            self.rows = [Item(x) for x in ('A', 'B', 'C')]
            self.current = self.rows[0]
            self.emitted = []
            self.orderChanged = SimpleNamespace(emit=self.emitted.append)
            self.viewport = lambda: SimpleNamespace(update=lambda: None)
        def values(self): return [item.value for item in self.rows]
        def currentItem(self): return self.current
        def indexOfTopLevelItem(self, item): return self.rows.index(item)
        def itemAt(self, point): return self.rows[2]
        def visualItemRect(self, item): return SimpleNamespace(center=lambda: SimpleNamespace(y=lambda: 50))
        def topLevelItemCount(self): return len(self.rows)
        def takeTopLevelItem(self, index): return self.rows.pop(index)
        def insertTopLevelItem(self, index, item): self.rows.insert(index, item)
        def setCurrentItem(self, item): self.current = item
        def _finish_root_reorder(self, *args): ns['_finish_root_reorder'](self, *args)

    tree = Tree()
    mouse = SimpleNamespace(toPoint=lambda: SimpleNamespace(y=lambda: 60))
    ignored = []
    event = SimpleNamespace(source=lambda: tree, position=lambda: mouse,
                            ignore=lambda: ignored.append(True))
    ns['dropEvent'](tree, event)
    assert ignored and tree.values() == ['A', 'B', 'C']
    assert len(scheduled) == 1
    scheduled.pop()()
    assert tree.values() == ['B', 'C', 'A']
    assert tree.emitted == [['B', 'C', 'A']]
