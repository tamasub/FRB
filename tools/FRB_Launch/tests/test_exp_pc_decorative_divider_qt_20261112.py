"""Qt geometry contract: the PC divider is ABOVE the native-height PC row.

Run on a Windows machine with PySide6; an offscreen Qt backend is sufficient.
The selection contract matters because wheel and Remote must skip decoration.
"""
import os
import pytest


def test_pc_has_normal_row_height_and_divider_is_skipped():
    if os.name != 'nt':
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    pytest.importorskip('PySide6')
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QApplication, QWidget, QStyle
    from pathlib import Path
    import sys

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'src'))
    from remote_files_explorer import FilesExpWheelTree, _DATA_ROLE

    app = QApplication.instance() or QApplication([])
    host = QWidget()
    model = QStandardItemModel(host)
    host.model = model
    tree = FilesExpWheelTree(host)
    tree.setModel(model)
    tree.setUniformRowHeights(False)
    tree.setHeaderHidden(True)

    normal = QStandardItem('FRB公開情報')
    normal.setData({'virtual': {'kind': 'page'}}, _DATA_ROLE)
    normal.setIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
    spacer = QStandardItem('')
    spacer.setFlags(Qt.ItemFlag.NoItemFlags)
    spacer.setData({'separator_before_pc': True}, _DATA_ROLE)
    spacer.setSizeHint(QSize(0, 19))
    pc = QStandardItem('PC')
    pc.setData({'pc': True, 'path': None}, _DATA_ROLE)
    pc.setIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
    model.appendRow(normal)
    model.appendRow(spacer)
    model.appendRow(pc)
    tree.resize(260, 240)
    tree.show()
    app.processEvents()
    i_normal, i_separator, i_pc = [model.index(i, 0) for i in range(3)]
    rect_normal, rect_separator, rect_pc = [tree.visualRect(i) for i in (i_normal, i_separator, i_pc)]
    assert not (i_separator.flags() & Qt.ItemFlag.ItemIsEnabled)
    assert tree._neighbor_operable(i_normal, 1) == i_pc
    assert tree._neighbor_operable(i_pc, -1) == i_normal
    assert rect_separator.height() == 19
    assert rect_pc.height() <= rect_normal.height() + 3, 'PC row must not be tall'
    assert rect_pc.top() == rect_separator.bottom() + 1
    tree.close()
    host.close()
