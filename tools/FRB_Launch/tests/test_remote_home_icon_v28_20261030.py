"""v28: Remote HOME should use exactly the same path icon as main Launch."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
remote = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
app = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def test_remote_home_uses_shared_vector_house_instead_of_folder_icon():
    assert "(self.nav_home_button, 'home')" in app
    assert "browser_navigation_icon('home', theme_family(launcher.color_theme))" in remote
    assert "browser_navigation_icon('home', theme_family(theme))" in remote
    assert 'SP_DirHomeIcon' not in remote
    assert 'QStyle.StandardPixmap' not in remote
    assert "self.home_button.setIconSize(QSize(18, 18))" in remote


def test_remote_home_keeps_original_semantics_and_compact_geometry():
    tree = ast.parse(remote)
    assert "'HOME', width=28, height=24, role='icon'" in remote
    assert "self.home_button.setObjectName('remoteHomeButton')" in remote
    assert 'self.home_button.setIcon(browser_navigation_icon(' in remote
    assert "self.home_button.setIcon(browser_navigation_icon('home', theme_family(theme)))" in remote
    assert "self.home_button" in remote
    assert "'CLOSE', width=22, height=22, role='icon'" in remote
    assert tree is not None
