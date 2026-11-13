# v0.14.32 ViewDef Header / Search Layout Rules Report

## 対象フェーズ

```text
v0.14.32-viewdef-header-search-layout-rules
```

## 更新対象

```text
data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json
data/json/00_rules/_json_creation_prompt.md
data/json/01_main/studio_work_incident_data_v0_61_viewdef_header_search_layout_rules_done.json
```

## 追加したViewDef生成ルール

```text
viewdef_rule_26    ヘッダー基本情報・検索項目コンパクト表示ポリシー
viewdef_rule_26_01 ヘッダー基本情報は1行に収まる範囲へ絞る
viewdef_rule_26_02 ヘッダー基本情報のマルチテキストボックスは表示オフを基本とする
viewdef_rule_26_03 ヘッダー基本情報 Owner は表示オフを基本とする
viewdef_rule_26_04 画面検索項目は縦マージンを調整してコンパクトにする
```

## 方針

ヘッダー部・基本情報は、詳細本文や長文説明を置く場所ではなく、現在のデータの文脈を一瞬で掴むための短い名札として扱う。

```text
ヘッダー基本情報:
  短い識別情報・状態・分類・日付などに絞る

長文項目:
  detailBody readable card / Markdown表示 / chat / objectArrayへ寄せる

Owner:
  ヘッダー基本情報では表示オフを基本とする

検索項目:
  必要項目に絞り、縦マージンを詰めすぎず太らせすぎずコンパクトにする
```

## 対象外

今回はルール更新が目的のため、既存ViewDefの一括修正、Runtime CSS修正、検索欄コンポーネント実装修正は対象外。
