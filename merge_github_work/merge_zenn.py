#!/usr/bin/env python3
"""
merge_zenn.py
Zenn記事(.md)を1コマンドでマージするスクリプト。

各ファイルについて:
  1. frontmatter (--- ... ---) から title を取り出す
  2. ファイル名 + title を見出しタグとして先頭に追加
  3. 本文中の見出し(# ~ ######)をすべて1段階(デフォルト)深くする
     (コードブロック ``` ~~~ の中の # はそのまま無視する)
  4. 全部つなげて1ファイルに出力する

使い方:
  python3 merge_zenn.py articles/*.md -o merged.md
  python3 merge_zenn.py a.md b.md c.md -o merged.md --shift 2

標準ライブラリのみで動作（Python 3.8+）。
"""

import argparse
import glob
import re
from pathlib import Path
from typing import Optional

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n?", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})(\s+)(.*)$")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def split_frontmatter(text: str):
    """先頭の --- ... --- ブロックと、残りの本文を分離する。"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def get_title(frontmatter: str) -> Optional[str]:
    """frontmatter から title: の値を取り出す（無ければ None）。"""
    for line in frontmatter.splitlines():
        line = line.strip()
        if line.lower().startswith("title:"):
            value = line.split(":", 1)[1].strip()
            return value.strip('"').strip("'")
    return None


def shift_headings(text: str, shift: int) -> str:
    """ATX見出し(#)をshift段階深くする。コードフェンス内は無視する。"""
    out_lines = []
    in_fence = False
    fence_marker = ""

    for line in text.splitlines():
        fence_match = FENCE_RE.match(line)
        if fence_match:
            # ``` と ~~~ のどちら系のフェンスかだけ判定する
            marker = fence_match.group(1)[0] * 3
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence, fence_marker = False, ""
            out_lines.append(line)
            continue

        if not in_fence:
            h = HEADING_RE.match(line)
            if h:
                hashes, sp, rest = h.groups()
                new_level = min(len(hashes) + shift, 6)  # h7以降は無いのでh6で止める
                line = "#" * new_level + sp + rest

        out_lines.append(line)

    return "\n".join(out_lines)


def build_tag(path: Path, title: Optional[str]) -> str:
    """ファイル名タグ（見出し）を作る。シフトの影響を受けないよう常にH1にする。"""
    label = title if title else path.stem
    return f"# 📄 {label}\n*(source: `{path.name}`)*\n"


def expand_inputs(raw_inputs, output_path: str):
    """PowerShellなどシェルがワイルドカード(*.md)を展開しない場合に備え、
    Python側でも glob 展開する。出力ファイル自身は誤って入力に含めない。
    """
    out_resolved = Path(output_path).resolve()
    expanded = []
    seen = set()

    for raw in raw_inputs:
        matches = sorted(glob.glob(raw))
        if not matches:
            # 展開できなければ「普通のファイル名」として扱う（既存の挙動を維持）
            matches = [raw]
        for m in matches:
            p = Path(m).resolve()
            if p == out_resolved:
                continue  # 出力ファイル自身を入力として再利用しない
            if p in seen:
                continue
            seen.add(p)
            expanded.append(m)

    return expanded


def main():
    ap = argparse.ArgumentParser(
        description="Zenn markdown を、ファイル名タグ付け＋見出しシフトしながら1ファイルにマージする。"
    )
    ap.add_argument("inputs", nargs="+", help="入力する .md ファイル（複数 / glob展開済み想定）")
    ap.add_argument("-o", "--output", default="merged.md", help="出力ファイル名（デフォルト: merged.md）")
    ap.add_argument("--shift", type=int, default=1, help="見出しを何段階深くするか（デフォルト: 1）")
    args = ap.parse_args()

    inputs = expand_inputs(args.inputs, args.output)
    if not inputs:
        raise SystemExit(
            "❌ 入力ファイルが見つかりませんでした。ファイル名やワイルドカードを確認してください。"
        )

    chunks = []
    for raw in inputs:
        path = Path(raw)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise SystemExit(f"❌ ファイルが見つかりません: {raw}")
        fm, body = split_frontmatter(text)
        title = get_title(fm)

        tag = build_tag(path, title)
        body_shifted = shift_headings(body, args.shift)

        chunks.append(f"{tag}\n{body_shifted.strip()}\n")

    merged = "\n\n---\n\n".join(chunks) + "\n"
    Path(args.output).write_text(merged, encoding="utf-8")
    print(f"✅ {len(inputs)} files -> {args.output}")


if __name__ == "__main__":
    main()