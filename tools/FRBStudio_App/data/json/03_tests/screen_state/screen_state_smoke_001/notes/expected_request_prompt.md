screen_state_smoke_001.expected.json に、
qa_expected_checks_classified_v0_1.json で追加したExpectedのうち、
screen_state_smoke_001 で確認できるものだけ checks に追記してください。

条件:
- 既存の checks 構造に合わせる
- check_id を追加して、Expected定義と紐づけられるようにする
- ncjs-screen-state-compare.checks.spec.ts 側も check_id を結果に残すようにする
- この画面状態JSONで確認できないExpectedは追加しない