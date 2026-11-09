# FRB Launch Public UI polish — とんとん親帰りエリア表記

- 日付: 2026-11-09
- 対象: `launch_app_20261109_200453.zip`

## 目的

Files List 左側の細い縦線をなくし、下部の空き領域を一つの L 字エリアとして見せたい。
その上で、Files List 側と Remote 側の両方に薄い案内文字
`～とんとん親帰りエリア～` を表示する。

## 変更内容

1. `src/expanded_view.py`
   - Files List 左の Back lane の右端セパレーター線を撤去。
   - Files List の空き領域に `～とんとん親帰りエリア～` を薄いグレーで表示する案内ラベルを追加。
   - 行数やスクロール量に応じて、空き領域へ自動配置するよう調整。

2. `src/launch_remote.py`
   - Remote の下部ダブルクリック帯のキャプションを
     `～とんとん親帰りエリア～` に変更。

## 確認ポイント

- Files List の左に縦線が出ないこと。
- Files List の下部空きエリアに薄い案内文字が出ること。
- Remote の青い帯の下に同じ案内文字が出ること。
- 項目が多い場合、Files List 側の案内文字が行と重なりにくいこと。
