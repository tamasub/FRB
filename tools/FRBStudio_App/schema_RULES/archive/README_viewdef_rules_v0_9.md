# README — ViewDef Rules v0.9

この版では、意味のある単位でFieldTypeを共通化するルールを追加した。

主な追加点:

- `relation.status / coverage / confidence / priority`
- `relation.relation_id / from_id / to_id`
- `business.customer_id / customer_name`
- `business.project_id / project_name`
- `business.employee_id / employee_name`
- 選択肢なしFieldTypeの標準化

スモールスタートの狙いは、ExpectedやViewDefを大量生成する前に、語彙と普通項目の標準形を固定すること。
