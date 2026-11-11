# FRB Launch × Studio Change Core 0269 — 複数登録解除・Move

- **対象基準**: `launch_app_20261111_205552(1).zip`
- **incident_file**: `data/json/01_main/_studio_work_incident_data_v2.json`
- **work_item_id**: `studio_work_0269`
- **phase**: `studio-external-changeset-core-v0_1`
- **位置付け**: Windows画面受入前。実機未検証部分を完了扱いにしない。

## 変更

1. LIST列で複数選択された **設定JSONの登録アイテム** を、1回の確認でまとめて登録解除する。配下もまとめて解除し、子のフォルダー数と末端メニューアイテム数を赤字警告する。保護対象・競合・失敗時は全件変更しない。
2. 設定JSONの登録アイテムを **ドラッグ＆ドロップで1件ずつMove**。LIST行の上端／下端で前後、カテゴリーの中央で配下、余白で現在のカテゴリー末尾へ移動。設定JSONのFiles Exp仮想フォルダー上へのDropはその配下へ移動。
3. **設定JSONのLIST列ではヘッダーソート禁止**。常に `sort_order` による表示。検索中はMove禁止。実ファイルの並べ替え・検索は従来どおり。

## 判断と制約

- Drop元・Drop先とも **Launch設定JSON由来** のみをMove対象とする。実ファイル・実フォルダー、Files Expに展開されたOSファイルシステム、実フォルダーの登録ルート、動的ブックマーク／アプリはMoveに使用しない。
- Move MIMEは `application/x-frb-launch-json-item-move-v1`。OSファイル／フォルダーCopyの `text/uri-list` と完全に分離し、QDrag元がLaunchのLIST/Files Expであることを検証する。
- Move実行は **確認応答なし**。Studio Change Coreの `dry_run → commit` とSHA競合判定を通し、直接ファイルを更新しない。
- Deleteは一括原子操作。実ファイルの削除は行わない。`System / Files` 内部管理ルートは保護する。
- Page自体のDelete、複数アイテム同時Move、OS実ファイルをDragして場所を移す機能は対象外。
- 登録（Add）用の既存ファイル・フォルダー・URLのDropは従来どおりCopyとして残す。

## 確認

- Studio Change Core Nodeテスト：37/37 PASS。
- Launch関連テスト：41/41 PASS（Node CLIによる一時JSONの実際のMove/複数Deleteを含む）。
- JSONの順番・Page/親・子孫維持、Expected/Actualの一致、SHA競合の拒否、実フォルダー内容保持を確認。
- Windows/PySide6の画面操作はこの環境で未確認。QtのDrag/Dropイベント実機受入が必要。

## 実機受入候補

1. 設定JSON LIST列でCtrl+クリックにより複数登録を選択 → 右クリック「登録解除（N件）」→ 1回のぐりぐり確認でまとめて解除。物理ファイルは残る。
2. 同じカテゴリーのアイテムA/B/CをドラッグしてA/C/Bの順番にする。Launch再起動後も維持。
3. 設定JSONカテゴリー中央にドロップ → その子になる。別Pageの仮想カテゴリー上でも移動可能。
4. 実ファイル・実フォルダーやFiles Exp物理ルートへのMoveを拒否する。既存の外部ファイルCopyと新規登録用Dropはそのまま。
5. JSON LISTのヘッダー「名前」「説明」「項目の種類」を押しても並び替わらず、物理LISTは通常のソートができる。
6. LIST検索中はMove不可。Move後にStudio画面でも親子・順序を確認。
