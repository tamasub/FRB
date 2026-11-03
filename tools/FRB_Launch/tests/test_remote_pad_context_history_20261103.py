"""Qt-free tests for Remote WheelPad's unified search/folder history menu."""
from test_remote_pad_context_nav_20261103 import Action, Menu, owner
from test_remote_pad_exp_return_20261103 import launcher, labels


def test_history_entries_follow_arrows_and_precede_original_menu():
    for original_name in ('フォルダーを開く', 'ファイルを開く', 'Launch JSON', 'Webメニュー'):
        app, pending = owner()
        menu = Menu()
        menu.addAction(Action(original_name))
        assert app._prepend_remote_pad_navigation(menu)
        assert [a.name for a in menu.actions()] == [
            '戻る', '進む', '---', '検索履歴', 'フォルダー履歴', '---', original_name]
        assert not app._prepend_remote_pad_navigation(menu)

        menu.popup((0, 0))
        menu.actions()[3].trigger()
        assert menu.closed == 1
        assert app.commands == []  # history popup cannot open under QMenu grab
        pending.pop(0)()
        assert app.commands == ['SEARCH_HISTORY']

        menu.popup((0, 0))
        menu.actions()[4].trigger()
        assert menu.closed == 2
        pending.pop(0)()
        assert app.commands == ['SEARCH_HISTORY', 'FOLDER_HISTORY']


def test_files_list_keeps_direct_exp_default_and_history_below_arrows():
    app, prepend, pending = launcher()
    menu = __import__('test_remote_pad_exp_return_20261103').Menu(['ファイルを開く'])
    assert prepend(menu)
    assert labels(menu) == [
        'Exp列に戻る', '---', '戻る', '進む', '---',
        '検索履歴', 'フォルダー履歴', '---', 'ファイルを開く']
    assert menu._remote_pad_initial_action.label == 'Exp列に戻る'
    menu.actions()[6].trigger()
    assert menu.closed == 1
    assert app.commands == []
    pending.pop(0)()
    assert app.commands == ['FOLDER_HISTORY']


def test_files_exp_keeps_back_default_with_history_available():
    app, prepend, pending = launcher(area='files_exp', target='files_exp')
    menu = __import__('test_remote_pad_exp_return_20261103').Menu(['Filesリスト'])
    menu.remote_context_root = True
    menu.remote_target_directory = r'F:\\FRB\\tools'
    assert prepend(menu)
    assert menu._remote_pad_initial_action.label == '戻る'
    assert labels(menu) == [
        '戻る', '進む', '---', '検索履歴', 'フォルダー履歴', '---', 'Filesリスト']
    menu.actions()[3].trigger()
    assert app.commands == []
    pending.pop(0)()
    assert app.commands == ['SEARCH_HISTORY']
