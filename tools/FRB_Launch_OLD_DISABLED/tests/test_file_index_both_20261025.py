"""FRB Launch: index eligible files *and the directories containing them*."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import file_index as fi

ROOT = Path(__file__).resolve().parents[1]


def _create_tree(tmp_path):
    root = tmp_path / 'workspace'
    # A single root with both matching files and excluded/noneligible files.
    (root / 'project' / 'src').mkdir(parents=True)
    (root / 'project' / 'src' / 'main.py').write_text('print(1)')
    (root / 'project' / 'README.md').write_text('hello')
    (root / 'project' / 'src' / 'other.txt').write_text('unsupported')
    (root / 'empty').mkdir()
    (root / 'only_txt').mkdir()
    (root / 'only_txt' / 'note.txt').write_text('no index')
    (root / 'build' / 'nested').mkdir(parents=True)
    (root / 'build' / 'nested' / 'bad.py').write_text('no index')
    (root / 'project' / 'exclude_view_def.json').write_text('{}')
    (root / 'project' / 'hidden.py').write_text('hide')
    (root / 'hiddenfolder').mkdir()
    (root / 'hiddenfolder' / 'inside.py').write_text('hide')
    (root / 'top.ps1').write_text('top')
    return root


def _assert_mixed_results(db, root):
    paths = {hit['path'] for hit in fi.search_index(db, 'workspace', limit=100)}
    want = {root, root / 'top.ps1', root / 'project', root / 'project' / 'README.md',
            root / 'project' / 'src', root / 'project' / 'src' / 'main.py'}
    assert paths == {str(p) for p in want}
    assert [hit['extension'] for hit in fi.search_index(db, 'top.ps1')] == ['.ps1']
    project = fi.search_index(db, 'project', entry_type='both')
    assert [hit['name'] for hit in project][:2] == ['project', 'src']
    assert fi.search_index(db, 'empty', entry_type='both') == []
    assert fi.search_index(db, 'only_txt', entry_type='both') == []
    assert not any(Path(hit['path']).is_relative_to(root / 'build') for hit in fi.search_index(db, 'build', entry_type='both'))
    assert fi.search_index(db, 'hidden', entry_type='both') == []
    assert fi.search_index(db, 'exclude_view_def.json', entry_type='both') == []


def test_incremental_mixed_index_excludes_unwanted_and_keeps_files(tmp_path):
    root = _create_tree(tmp_path)
    opts = fi.load_options(tmp_path / 'not_found.json')
    opts['index_target'] = 'both'
    db = tmp_path / 'index.db'
    with patch.object(fi, 'is_hidden_attribute', side_effect=lambda path: Path(path).name in ('hidden.py', 'hiddenfolder')):
        result = fi.refresh_index(db, [str(root)], opts)
        assert result['count'] == 6
        _assert_mixed_results(db, root)
        assert fi.search_index(db, 'project', limit=1, entry_type='both')[0]['name'] == 'project'
        assert fi.refresh_index(db, [str(root)], opts)['changed_roots'] == []
        # File updates are reflected in both the file row and its parent directory.
        (root / 'project' / 'README.md').unlink()
        changed = fi.refresh_index(db, [str(root)], opts)
        assert changed['changed_roots'] == [str(root)]
        assert fi.search_index(db, 'README.md', entry_type='both') == []
        assert 'project' not in {p['name'] for p in fi.search_index(db, 'project', entry_type='both')}
        assert 'src' in {p['name'] for p in fi.search_index(db, 'project', entry_type='both')}
        (root / 'project' / 'src' / 'main.py').unlink()
        fi.refresh_index(db, [str(root)], opts)
        assert fi.search_index(db, 'src', entry_type='both') == []
        assert fi.search_index(db, 'project', entry_type='both') == []


def test_legacy_full_index_build_both_targets(tmp_path):
    root = _create_tree(tmp_path)
    options = fi.load_options(tmp_path / 'missing.json')
    options['index_target'] = 'both'
    db = tmp_path / 'legacy.db'
    with patch.object(fi, 'is_hidden_attribute', side_effect=lambda path: Path(path).name in ('hidden.py', 'hiddenfolder')):
        result = fi.build_index(db, [str(root)], options)
        assert result['count'] == 6
        _assert_mixed_results(db, root)


def test_options_switch_from_folders_triggers_reindex_and_legacy_modes_remain(tmp_path):
    root = tmp_path / 'workspace'
    child = root / 'src'
    child.mkdir(parents=True)
    (child / 'main.py').write_text('hello')
    (root / 'alone').mkdir()
    db = tmp_path / 'index.db'
    options = fi.load_options(tmp_path / 'missing.json')
    options['index_target'] = 'folders'
    fi.refresh_index(db, [str(root)], options)
    assert fi.search_index(db, 'main.py') == []
    assert fi.search_index(db, 'alone', entry_type='folders')
    options['index_target'] = 'both'
    assert fi.refresh_index(db, [str(root)], options)['changed_roots'] == [str(root)]
    assert fi.search_index(db, 'main.py', entry_type='both')
    assert fi.search_index(db, 'src', entry_type='both')
    assert fi.search_index(db, 'alone', entry_type='both') == []
    options['index_target'] = 'files'
    fi.refresh_index(db, [str(root)], options)
    assert fi.search_index(db, 'main.py', entry_type='files')
    assert not any(hit['name'] == 'src' for hit in fi.search_index(db, 'src', entry_type='files'))


def test_config_and_launcher_search_branch_support_mixed_results(tmp_path):
    config = json.loads((ROOT / 'config/file_index_options.json').read_text(encoding='utf-8'))
    assert config['index_target'] == 'both'
    assert fi.load_options(ROOT / 'config/file_index_options.json')['index_target'] == 'both'
    app_source = (ROOT / 'src/app.py').read_text(encoding='utf8')
    ast.parse(app_source)
    assert "is_folder = hit['extension'] == ''" in app_source
    assert "pairs.append((row, 'フォルダー索引'))" in app_source
    assert "pairs.append((row, 'ファイル索引'))" in app_source


def test_actual_launcher_search_row_mapping_for_both_kinds(tmp_path):
    """Exercise the actual row-creation loop without loading the Qt window."""
    root = tmp_path / 'workspace'
    project = root / 'project'
    project.mkdir(parents=True)
    (project / 'main.py').write_text('hello')
    options = fi.load_options(tmp_path / 'missing.json')
    options['index_target'] = 'both'
    db = tmp_path / 'index.db'
    fi.refresh_index(db, [str(root)], options)
    source = (ROOT / 'src/app.py').read_text(encoding='utf8')
    tree = ast.parse(source)
    loop = next(node for node in ast.walk(tree)
                if isinstance(node, ast.For) and
                isinstance(node.iter, ast.Call) and
                isinstance(node.iter.func, ast.Attribute) and
                node.iter.func.attr == 'search_index')
    code = compile(ast.fix_missing_locations(ast.Module(body=[loop], type_ignores=[])),
                   'src/app.py', 'exec')
    context = {
        'self': SimpleNamespace(file_index_settings={**options, 'search_limit': 100}, file_index_db=db),
        'query': 'project', 'pairs': [], 'file_index': fi
    }
    exec(code, context)
    pairs = context['pairs']
    files = [row for row, source in pairs if source == 'ファイル索引']
    folders = [row for row, source in pairs if source == 'フォルダー索引']
    assert len(files) == len(folders) == 1
    assert files[0]['item_kind'] == 'command'
    assert files[0]['_indexed_file'] == str(project / 'main.py')
    assert folders[0]['item_kind'] == 'directory'
    assert folders[0]['launch_browse_target'] == str(project)
