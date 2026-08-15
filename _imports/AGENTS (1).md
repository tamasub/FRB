# AGENTS.md

## Project Mission

このリポジトリの目的は、

> 最近の日本のヒット曲を取得し、公式または正当な権利者が公開している
> YouTube動画を特定し、人間が確認・再生しやすい形で構造化すること。

主目的は動画ファイルのダウンロードではない。

---

## Core Principle

```text
Find first.
Verify second.
Structure third.
Download only when explicitly allowed.
```

日本語では次の意味とする。

```text
まず見つける。
次に確認する。
その後、構造化する。
明示的に許可されている場合だけ保存する。
```

---

## Decision Axes

判断に迷った場合は、以下を上位判断軸とする。

1. 権利・利用条件を守る
2. 公式性・出典を追跡できる
3. 誤判定を減らす
4. 再現可能な処理にする
5. 人間が確認しやすくする
6. 自動化する
7. 処理速度を上げる

下位の目的のために、上位判断軸を破ってはならない。

---

## Hard Constraints

### C001 — Unauthorized Download Prohibited

著作権者の許可や明示された利用条件を確認できない
YouTube動画・音声を自動ダウンロードしてはならない。

---

### C002 — No Access-Control Circumvention

以下を実装してはならない。

- DRM回避
- アクセス制御回避
- 有料・限定公開コンテンツの取得回避
- サービス側の保護機構を回避する処理

---

### C003 — Discovery Is Not Permission

```text
動画URLを取得できた
≠
ダウンロードしてよい
```

検索成功を保存許可として扱ってはならない。

---

### C004 — Unknown Means No Download

ダウンロード可否が不明な場合、

```json
"download_allowed": false
```

または

```json
"download_status": "UNKNOWN"
```

として扱う。

不明状態を `true` に推測してはならない。

---

### C005 — Officiality Must Be Traceable

動画を公式として扱う場合は、判定根拠を可能な範囲でデータとして残す。

例:

```json
{
  "official_status": "LIKELY_OFFICIAL",
  "official_reason": [
    "artist_name_matches_channel",
    "video_title_matches_song"
  ]
}
```

---

### C006 — AI Agreement Is Not Human Approval

複数のAIや複数の判定ロジックが一致しても、
それだけで権利・利用許可が確定したとはみなさない。

---

## Responsibilities

### Chart Collector

責務:

- 最近の日本のヒット曲を取得する
- 順位・曲名・アーティスト・基準日を保存する

責務外:

- YouTube動画を決定する
- 動画をダウンロードする

---

### YouTube Searcher

責務:

- 曲名＋アーティストから候補動画を探す
- URL、タイトル、チャンネル等を取得する

責務外:

- 公式動画だと最終確定する
- ダウンロード許可を判断する

---

### Official Resolver

責務:

- 動画候補の公式性を評価する
- 判定理由を残す

想定状態:

```text
CONFIRMED_OFFICIAL
LIKELY_OFFICIAL
UNRESOLVED
REJECTED
```

不明な場合は `UNRESOLVED` を選ぶ。

---

### Output Builder

責務:

- JSON
- CSV
- HTML

など、人間が確認しやすい成果物を生成する。

---

### Download Worker

通常は無効とする。

責務:

- `download_allowed = true` の対象だけを処理する

禁止:

- 自分で許可を推測して `true` へ変更する
- URLが存在するという理由だけで保存する

---

## Expected Data Model

最低限、次の情報を保持する。

```json
{
  "rank": 1,
  "title": "",
  "artist": "",
  "chart_source": "",
  "chart_date": "",
  "youtube_url": "",
  "video_title": "",
  "channel": "",
  "official_status": "UNRESOLVED",
  "official_reason": [],
  "download_allowed": false,
  "download_permission_reason": "",
  "checked_at": ""
}
```

項目を追加してよいが、意味の異なる項目を一つに混ぜない。

---

## Development Rules

### Before Editing

作業開始時は必ず以下を確認する。

1. `README.md`
2. `AGENTS.md`
3. 既存ディレクトリ構成
4. 既存テスト
5. 既存設定ファイル

既存設計を読まずに全面書き換えしない。

---

### Small Changes

変更はできるだけ責務単位で小さく行う。

```text
Chart取得
YouTube検索
公式判定
Output
Download判定
```

を一つの巨大関数にまとめない。

---

### External Access

外部サイト・APIを利用するコードを追加する場合は、

- 利用目的
- 対象ドメイン
- 取得データ
- 保存データ

が追跡できる構造にする。

取得できない場合に無理な回避策を実装しない。

---

### Configuration First

以下のような値は可能な限り設定へ外出しする。

```text
Top N
chart source
output directory
request interval
official confidence threshold
HTML output enabled
```

コードへ無意味にハードコードしない。

---

## Testing

最低限、以下をテスト可能にする。

### Chart

- 正常データを読み込める
- 曲名がないデータを拒否できる
- アーティスト名がないデータを扱える

### Search

- 検索語を正規化できる
- 候補0件を正常状態として扱える
- 重複URLを排除できる

### Resolver

- 公式候補を評価できる
- 不明時に `UNRESOLVED` になる
- 非公式候補を拒否できる

### Download Gate

最重要。

```text
download_allowed = false
→ Download Worker は絶対に実行しない

download_status = UNKNOWN
→ Download Worker は絶対に実行しない

download_allowed = true
→ 許可根拠が存在することを確認する
```

---

## Human Approval Gate

次の変更は人間確認対象とする。

- Download Workerの有効化
- ダウンロード条件の変更
- 権利判定ロジックの緩和
- 新しい外部サービスへのアクセス
- 大量アクセスにつながる変更
- 既存Hard Constraintの削除・緩和

AI単独で制約を弱めない。

---

## Logging

重要な処理では、少なくとも次を追跡可能にする。

```text
いつ
何を検索したか
どの候補を得たか
なぜ採用したか
なぜ拒否したか
ダウンロード可否をどう判断したか
```

---

## Failure Policy

迷った場合は安全側へ倒す。

```text
公式か不明
→ UNRESOLVED

保存可能か不明
→ download_allowed = false

データソース取得失敗
→ エラーとして記録

検索結果なし
→ 正常な0件結果として記録
```

推測で穴埋めしない。

---

## Git / Change Policy

Codexは、ユーザーから明示的な依頼がない限り、

- 勝手に大規模リファクタリングしない
- 既存仕様を削除しない
- Hard Constraintを変更しない
- commit / push を前提にしない

変更後は、

```text
変更内容
変更理由
実行したテスト
残っているリスク
```

を簡潔に報告する。

---

## v0.1 Goal

v0.1では、次の状態を完成とする。

```text
最近の日本のヒット曲 Top N 取得
↓
JSON化
↓
YouTube候補検索
↓
公式候補判定
↓
hits.json生成
↓
HTML一覧生成
↓
クリックしてYouTube再生
```

動画ファイルのダウンロードは v0.1 の必須機能ではない。

---

## Final Rule

このプロジェクトで最も重要な制約:

> **見つけられることと、保存してよいことを混同しない。**
