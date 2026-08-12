from pathlib import Path

# ==============================
# 設定
# ==============================

# 調べたいフォルダー
TARGET_DIR = Path(r"F:\FRB\tools\FRBStudio_App")

# 出力ファイル
OUTPUT_FILE = TARGET_DIR / "cmd_file_size_list.txt"


def format_size(size_bytes):
    """ファイルサイズを見やすい形式に変換"""
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):10.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):10.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:10.2f} KB"
    else:
        return f"{size_bytes:10d} B"


# ==============================
# ファイル取得
# ==============================

files = []

for file_path in TARGET_DIR.rglob("*"):
    if not file_path.is_file():
        continue

    # 出力ファイル自身は除外
    if file_path == OUTPUT_FILE:
        continue

    try:
        size = file_path.stat().st_size
        files.append((size, file_path))
    except (PermissionError, OSError):
        print(f"取得できませんでした: {file_path}")


# ==============================
# サイズ降順
# ==============================

files.sort(key=lambda x: x[0], reverse=True)


# ==============================
# テキスト出力
# ==============================

with OUTPUT_FILE.open("w", encoding="utf-8-sig") as f:
    f.write(f"対象フォルダー: {TARGET_DIR}\n")
    f.write(f"ファイル数    : {len(files)}\n")
    f.write("=" * 120 + "\n")

    for size, file_path in files:
        relative_path = file_path.relative_to(TARGET_DIR)

        f.write(
            f"{format_size(size)}  "
            f"{size:15,d} bytes  "
            f"{relative_path}\n"
        )


print(f"完了: {OUTPUT_FILE}")