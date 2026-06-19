# ViewDef extends demo 001

同じ `fft_log_sample.json` を、ViewDef差分だけで別表示にするデモです。

## 追加ファイル

- `defs/fft_log_view_def_v0_2.json`  
  親ViewDef

- `defs/fft_log_view_def_v0_2_peak_focus.json`  
  `extends` で親を継承し、主ピーク・メロディ寄りの表示へ差分上書き

- `defs/fft_log_view_def_v0_2_phase2_focus.json`  
  `extends` で親を継承し、Phase2 / Attack寄りの表示へ差分上書き

## 使い方

1. `app.js`, `index.html`, `styles.css` を `wwwroot` 直下へコピー
2. `defs/*.json` を `wwwroot/defs` へコピー
3. `data/fft_log_sample.json` を `wwwroot/data` へコピー
4. No-Code JSON Studioを開く
5. 対象JSONに `fft_log_sample.json` を選ぶ
6. 画面定義JSONを以下で切り替える
   - `fft_log_view_def_v0_2.json`
   - `fft_log_view_def_v0_2_peak_focus.json`
   - `fft_log_view_def_v0_2_phase2_focus.json`

## 実装メモ

- `extends` は画面定義JSONのルートに書く
- 親ViewDefを読み、子ViewDefの差分で上書きする
- `views` は `id` でマージ
- `sections` は `id` でマージ
- `fields` は `field` でマージ
- `options` などの単純配列は子で置換

```json
{
  "extends": "fft_log_view_def_v0_2.json",
  "views": [
    {
      "id": "fft_log_main",
      "caption": "FFT Log Viewer / Peak Focus（差分View）",
      "sections": [
        {
          "id": "tsBuf",
          "fields": [
            {
              "field": "bandA.b0",
              "grid": { "visible": false },
              "edit": { "visible": false }
            }
          ]
        }
      ]
    }
  ]
}
```
