#!/usr/bin/env python3
# count_js_steps.py
#
# JSファイルのステップ数を数える簡易ツール。
# - サブフォルダー配下の .js を再帰的に対象
# - 空白行は除外
# - コメントだけの行は除外
# - 行末コメント付きのコード行は「コード行」としてカウント
#
# 使い方:
#   python count_js_steps.py
#   python count_js_steps.py wwwroot
#   python count_js_steps.py wwwroot --csv js_steps.csv
#   python count_js_steps.py wwwroot --json js_steps.json
#
# 注意:
#   JSの構文を完全解析するものではありません。
#   ただし通常の // コメント、/* ... */ コメント、文字列中の // や /* は考慮します。

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path


DEFAULT_EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    ".vs",
    ".vscode",
    "bin",
    "obj",
    "dist",
    "build",
}


@dataclass
class FileCount:
    path: str
    total_lines: int
    blank_lines: int
    comment_only_lines: int
    code_lines: int


def line_without_comments(
    line: str,
    *,
    in_block_comment: bool,
    in_string: str | None,
    escape: bool,
) -> tuple[str, bool, str | None, bool, bool]:
    """
    1行からコメント部分を除いた文字列を返す。

    returns:
      code_part,
      next_in_block_comment,
      next_in_string,
      next_escape,
      line_had_comment_text_only_candidate

    line_had_comment_text_only_candidate は、
    コメント記号を見つけたかどうかの目安。
    最終的な comment_only 判定は呼び出し側で行う。
    """
    out: list[str] = []
    i = 0
    saw_comment = False

    while i < len(line):
        ch = line[i]
        nxt = line[i + 1] if i + 1 < len(line) else ""

        if in_block_comment:
            saw_comment = True
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if in_string is not None:
            out.append(ch)

            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None

            i += 1
            continue

        # 文字列開始
        if ch in ("'", '"', "`"):
            in_string = ch
            out.append(ch)
            i += 1
            continue

        # 行コメント開始
        if ch == "/" and nxt == "/":
            saw_comment = True
            break

        # ブロックコメント開始
        if ch == "/" and nxt == "*":
            saw_comment = True
            in_block_comment = True
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out), in_block_comment, in_string, escape, saw_comment


def count_js_file(path: Path, root: Path) -> FileCount:
    total = 0
    blank = 0
    comment_only = 0
    code = 0

    in_block_comment = False
    in_string: str | None = None
    escape = False

    text = path.read_text(encoding="utf-8-sig", errors="replace")

    for raw_line in text.splitlines():
        total += 1

        if not raw_line.strip():
            blank += 1
            continue

        before_in_block = in_block_comment
        code_part, in_block_comment, in_string, escape, saw_comment = line_without_comments(
            raw_line,
            in_block_comment=in_block_comment,
            in_string=in_string,
            escape=escape,
        )

        if code_part.strip():
            code += 1
        else:
            # 空白ではないが、コメント除去後に何も残らない行
            # 例: // xxx, /* xxx */, ブロックコメント中の行
            if saw_comment or before_in_block:
                comment_only += 1
            else:
                # 念のため。実質的には空白扱い。
                blank += 1

    rel = path.relative_to(root).as_posix()
    return FileCount(
        path=rel,
        total_lines=total,
        blank_lines=blank,
        comment_only_lines=comment_only,
        code_lines=code,
    )


def iter_js_files(root: Path, include_minified: bool, exclude_dirs: set[str]) -> list[Path]:
    files: list[Path] = []

    for path in root.rglob("*.js"):
        parts = set(path.relative_to(root).parts)

        if parts & exclude_dirs:
            continue

        if not include_minified and path.name.endswith(".min.js"):
            continue

        files.append(path)

    return sorted(files, key=lambda p: p.as_posix().lower())


def print_table(rows: list[FileCount]) -> None:
    if not rows:
        print("対象の .js ファイルがありません。")
        return

    path_width = max(len("file"), *(len(r.path) for r in rows))
    header = (
        f"{'file'.ljust(path_width)}  "
        f"{'code':>6}  {'blank':>6}  {'comment':>7}  {'total':>6}"
    )
    print(header)
    print("-" * len(header))

    for r in rows:
        print(
            f"{r.path.ljust(path_width)}  "
            f"{r.code_lines:>6}  {r.blank_lines:>6}  "
            f"{r.comment_only_lines:>7}  {r.total_lines:>6}"
        )

    total_code = sum(r.code_lines for r in rows)
    total_blank = sum(r.blank_lines for r in rows)
    total_comment = sum(r.comment_only_lines for r in rows)
    total_lines = sum(r.total_lines for r in rows)

    print("-" * len(header))
    print(
        f"{'TOTAL'.ljust(path_width)}  "
        f"{total_code:>6}  {total_blank:>6}  {total_comment:>7}  {total_lines:>6}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="サブフォルダー配下の .js を対象に、空白行・コメント行を除いたステップ数を数えます。"
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="集計対象フォルダー。省略時はカレントフォルダー。",
    )
    parser.add_argument(
        "--include-minified",
        action="store_true",
        help=".min.js も対象に含める。",
    )
    parser.add_argument(
        "--include-node-modules",
        action="store_true",
        help="node_modules も対象に含める。",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="",
        help="CSV出力先ファイル。",
    )
    parser.add_argument(
        "--json",
        type=str,
        default="",
        help="JSON出力先ファイル。",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"対象フォルダーが存在しません: {root}")

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    if args.include_node_modules:
        exclude_dirs.discard("node_modules")

    files = iter_js_files(root, args.include_minified, exclude_dirs)
    rows = [count_js_file(path, root) for path in files]

    print_table(rows)

    if args.csv:
        csv_path = Path(args.csv)
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["path", "code_lines", "blank_lines", "comment_only_lines", "total_lines"],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(asdict(row))
        print(f"\nCSVを書き出しました: {csv_path}")

    if args.json:
        json_path = Path(args.json)
        payload = {
            "root": str(root),
            "file_count": len(rows),
            "total_code_lines": sum(r.code_lines for r in rows),
            "total_blank_lines": sum(r.blank_lines for r in rows),
            "total_comment_only_lines": sum(r.comment_only_lines for r in rows),
            "total_lines": sum(r.total_lines for r in rows),
            "files": [asdict(r) for r in rows],
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSONを書き出しました: {json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
