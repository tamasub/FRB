from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scroll_icon_asset_exists_and_source_references_it():
    asset = ROOT / 'assets' / 'remote_shuriken_scroll.png'
    assert asset.exists()
    source = (ROOT / 'src' / 'remote_shuriken_scroll.py').read_text('utf-8')
    assert "remote_shuriken_scroll.png" in source
    assert "remoteShurikenScrollIcon" in source

