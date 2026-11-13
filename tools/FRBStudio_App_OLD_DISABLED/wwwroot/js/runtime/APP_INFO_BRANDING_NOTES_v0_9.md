# APP_INFO_BRANDING_NOTES_v0_9

## Summary

v0.9-json-object-studio-branding では、画面上の正式名称を `FRB Studio / JSON Object Studio` へ切り替えた。

## Files

- `config/app_info.json`
  - brand / product / version / revision / display_version / tagline を持つアプリ名札。
- `config/app_settings.json`
  - 将来の動作設定分離用の雛形。
- `index.html`
  - 初期表示を正式名称に変更し、app_info適用用のidを追加。
- `js/ui/page_setup.js`
  - app_info読込とヘッダー反映処理を追加。

## Policy

`app_info.json` は「今このアプリは何者か」を示す名札に限定する。
動作設定・履歴・インシデント詳細は混在させない。
