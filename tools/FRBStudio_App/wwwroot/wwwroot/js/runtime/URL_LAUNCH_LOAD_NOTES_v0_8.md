# URL Launch Load Notes v0.8

## 目的

記事・README・MarkdownからURLをクリックするだけで、Studioくんが指定されたData JSON / ViewDef JSON / Markdownを起動時に自動読込する。

## index.html

対応パラメータ:

```text
index.html?data=data/json/01_main/sample.json&view=defs/sample_view_def.json
index.html?data=data/json/01_main/sample.json
index.html?data=json/01_main/sample.json&view=sample_view_def.json
index.html?data=data/json/01_main/sample.json&view=defs/sample_view_def.json&mode=readonly
```

### 読込順

1. `data` を必須とする。
2. `view` または `def` があれば明示ViewDefとして優先する。
3. `view` / `def` がなければ Data JSON 内の `view_def` を使う。
4. Data内 `view_def` がない場合は既存の自動ViewDef推定に委譲する。

## mdViewer.html

対応パラメータ:

```text
mdViewer.html?file=FRB_Lab_Notes_Qiita.md
mdViewer.html?file=data/markdown/FRB_Lab_Notes_Qiita.md
mdViewer.html?md=FRB_Lab_Notes_Qiita.md&mode=readonly
```

## 安全制約

以下は拒否する。

- `http://` / `https://` などの外部URL
- `//example.com` 形式
- `/data/...` のような絶対パス
- `C:/...` のようなローカルドライブパス
- `../` による親ディレクトリ参照
- `?` / `#` を含む追加クエリ

## ReadOnly

`mode=readonly` の場合、起動読込後に保存・編集系の主要操作を抑制する。

- index.html: 保存、追加、削除、詳細反映、貼り付けを抑制
- mdViewer.html: editorをreadOnly化し、保存・上書き・ローカル読込・クリップボード流し込みを抑制

## v0.8でやらないこと

- URLからのAction自動実行
- Replay起動
- step指定ジャンプ
- 外部URLからのJSON読込
- 完全な公開サイト用権限制御

---

# v0.8.1 GitHub Pages Static Launch

## 目的

GitHub Pagesなどの静的ホスティング環境では、FRBStudio.exe の `/api/defs/...` / `/api/data/...` が存在しない。
そのため、URL起動やData内 `view_def` 自動解決時に、静的ファイルとして `wwwroot` 配下を直接参照する。

## 静的ホスティング判定

以下では `/api` を前提にせず、静的ファイル探索を優先する。

```text
location.protocol === "file:"
location.hostname.endsWith("github.io")
localhost / 127.0.0.1 / ::1 以外の http(s)
```

## ViewDef探索

Data JSON内に次のような指定がある場合:

```json
{
  "view_def": "studio_work_incident_view_def_v0_2_readable_cards.json"
}
```

GitHub Pages上では、次の候補を静的ファイルとして探索する。

```text
defs/studio_work_incident_view_def_v0_2_readable_cards.json
defs/studio/studio_work_incident_view_def_v0_2_readable_cards.json
defs/json/studio_work_incident_view_def_v0_2_readable_cards.json
```

## Data探索

Data JSONについても、必要に応じて次の候補を静的ファイルとして探索する。

```text
data/<name>
data/json/<name>
```

## 方針

- ローカルFRBStudio.exeでは従来どおり `/api` を優先する。
- GitHub Pagesでは `/api` へアクセスせず、静的ファイルとして読み込む。
- 静的ホスティングで読み込んだDataは上書き保存できないため、`dataApiUrl` は `null` とし、保存時は別名保存側へ倒す。
