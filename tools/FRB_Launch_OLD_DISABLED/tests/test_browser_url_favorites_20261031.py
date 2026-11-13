"""Browser URL favorites: persistence, safety and Remote wiring."""
import ast
import json
from pathlib import Path

from browser_url_favorites import BrowserUrlFavorites, normalize_favorite_url


ROOT = Path(__file__).resolve().parents[1] / 'src'


def test_url_validation_does_not_persist_non_web_schemes():
    assert normalize_favorite_url('https://example.com/a?q=日本語#test') == 'https://example.com/a?q=日本語#test'
    assert normalize_favorite_url(' http://example.com/path ') == 'http://example.com/path'
    for bad in ('', 'file:///C:/Users/', 'javascript:alert(1)', 'data:text/html,Hi',
                'http://', 'http://example.com:invalid', 'https://bad host/x',
                'ftp://example.com', 'relative/file.html', 'https://example.com\nanything'):
        assert normalize_favorite_url(bad) == ''


def test_add_delete_restart_and_atomic_json(tmp_path):
    path = tmp_path / 'browser_url_favorites.json'
    store = BrowserUrlFavorites(path, limit=3)
    assert store.add('https://example.com/a')
    assert not store.add('https://example.com/a')
    assert store.add('https://example.com/日本語')
    assert store.add('https://another.example/')
    assert store.add('https://fourth.example/')
    assert store.urls == ['https://fourth.example/', 'https://another.example/',
                          'https://example.com/日本語']
    assert json.loads(path.read_text(encoding='utf-8'))['urls'] == store.urls
    restored = BrowserUrlFavorites(path, limit=3)
    assert restored.urls == store.urls
    assert restored.remove('https://another.example/')
    assert not restored.remove('https://nonexistent.example')
    assert BrowserUrlFavorites(path).urls == ['https://fourth.example/',
                                                'https://example.com/日本語']
    assert restored.reorder(list(reversed(restored.urls)))
    assert BrowserUrlFavorites(path).urls == list(reversed(store.urls[:1] + [store.urls[2]]))


def test_invalid_corrupt_json_and_duplicate_load(tmp_path):
    path = tmp_path / 'favorites.json'
    path.write_text('{bad json', encoding='utf-8')
    assert BrowserUrlFavorites(path).urls == []
    path.write_text(json.dumps({'urls': ['https://good.example', 'file:///bad',
                                         'https://good.example', 25, 'http://other.example']}),
                    encoding='utf-8')
    assert BrowserUrlFavorites(path).urls == ['https://good.example', 'http://other.example']


def test_ui_and_remote_connections_are_shared():
    web = (ROOT / 'launch_web_view.py').read_text(encoding='utf-8')
    app = (ROOT / 'app.py').read_text(encoding='utf-8')
    remote = (ROOT / 'launch_remote.py').read_text(encoding='utf-8')
    for source in (web, app, remote):
        ast.parse(source)
    assert "'FRBLaunch' / 'browser_url_favorites.json'" in web
    assert 'self.favorite_save.clicked.connect(self.register_url_favorite)' in web
    assert 'self.favorite_dropdown.clicked.connect(self.toggle_url_favorites)' in web
    assert 'self.favorite_choices.itemClicked.connect(self.url_favorite_clicked)' in web
    assert 'self.url_favorites.remove(url)' in web
    assert 'self.url_favorites.reorder(urls)' in web
    assert "if command == 'FOLDER_HISTORY':" in app
    assert "if browser_mode:" in app
    assert "self._remote_popup_area = 'browser_history'" in app
    assert 'web.url_favorite_clicked(row, 0)' in app
    assert "'browser_history': 'URLお気に入り'" in remote
