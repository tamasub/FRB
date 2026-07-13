# Studio Overlay default

このフォルダーは、Studio Core を変更せずに会社・勇者側の追加定義を重ねるための領域です。

## 編集ルール

- `wwwroot/` は Core です。Copilotは触りません。
- `data/json/00_rules/common_enums_v0_1.json` は Core の値語彙正本です。Copilotは触りません。
- 会社固有のコード、資格、ランク、業務知識、ViewDef、検索パターン、Pluginは `studio_overlays/default/` 配下に追加します。
- Coreとの会話は `studio_manifest.json` に宣言します。

## 合言葉

Coreは触るな。defaultに重ねろ。会話はmanifestでやれ。
