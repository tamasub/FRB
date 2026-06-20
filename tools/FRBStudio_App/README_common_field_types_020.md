# FRBStudio Common FieldTypes 020

019の修正版です。現行APIで `defs/common/common_types_v0_1.json` のようなサブフォルダ読み込みが失敗する環境向けに、共通Type定義を `defs/common_types_v0_1.json` として読む形に変更しました。

- `defs/common_types_v0_1.json` を追加
- `defs/common/common_types_v0_1.json` も互換用に残置
- `fieldTypeSources` は `common_types_v0_1.json` に変更
- `app.js` はサブフォルダ指定失敗時に basename へフォールバック

確認ポイント:

- `qa_expected_checks_sample_view_def_v0_1.json` がエラーなく読める
- `quality_axis_cd` が日本語ラベル表示・CD保存になる
- 既存の文字列optionsは従来通り動く
