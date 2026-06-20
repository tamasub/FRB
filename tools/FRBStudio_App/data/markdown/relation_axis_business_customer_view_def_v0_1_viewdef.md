# ViewDef定義レポート — relation_axis_business_customer / 顧客軸

## 基本情報
- 出力日時: 2026/6/20 19:09:16
- 対象ViewDef: relation_axis_business_customer_view_def_v0_1.json
- app.name: No-Code JSON Studio
- app.version: 0.5-relation-business-sample
- views: 1

## View / Section 概要
| View | View Caption | Section | Section Caption | Type | DataPath | KeyField | Fields |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| relation_axis_business_customer | relation_axis_business_customer / 顧客軸 | header | Business Relation / 基本情報 | form | $ |  | 4 |
| relation_axis_business_customer | relation_axis_business_customer / 顧客軸 | main_grid | relation_axis_business_customer / 顧客軸 | grid | $.relation_axis_business_customer_cards | customer_id | 9 |

## 継承差分サマリ

このViewDefは extends を持たないため、継承差分はありません。

## relation_axis_business_customer / 顧客軸

- view.id: relation_axis_business_customer
- layout: header-search-grid-detail

### Business Relation / 基本情報

- section.id: header
- type: form
- dataPath: $
- fields: 4

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| title | タイトル | text | false | 220 | true | true |  |  |
| schema_version | Schema | text | false | 120 | true | true |  |  |
| document_type | Document Type | text | false | 170 | true | true |  |  |
| note | メモ | textarea | false | 260 | true | true |  |  |

### relation_axis_business_customer / 顧客軸

- section.id: main_grid
- type: grid
- dataPath: $.relation_axis_business_customer_cards
- keyField: customer_id
- fields: 9

| field | caption | type | grid.visible | width | edit.visible | readonly | search | options |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| customer_id |  | text | true | 110 |  | true |  |  |
| customer_name |  | text | true | 180 |  | false |  |  |
| trace_label |  | text | true | 120 |  | true |  |  |
| project_count |  | text | true | 80 |  | true |  |  |
| primary_count |  | text | true | 70 |  | true |  |  |
| secondary_count |  | text | true | 70 |  | true |  |  |
| coverage | Coverage | text | true | 110 | true | true | true (contains) |  |
| related_projects | 関連案件 | objectArray | false |  | true | true |  |  |
| evidence_edges | 証跡エッジ | objectArray | false |  | true | true |  |  |

---

## ViewDef JSON

<details>
<summary>元ViewDef JSONを表示</summary>

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.5-relation-business-sample"
  },
  "dataSources": {
    "customers": "business_customers_v0_1.json",
    "projects": "business_projects_v0_1.json",
    "tasks": "business_tasks_v0_1.json",
    "employees": "business_employees_v0_1.json",
    "relations": "business_relations_v0_1.json"
  },
  "writePolicy": {
    "mode": "singleSource",
    "primarySource": "customers",
    "virtualDataReadonly": false,
    "editableSources": [
      "customers"
    ],
    "readonlySources": [
      "projects",
      "tasks",
      "employees",
      "relations"
    ]
  },
  "virtualData": {
    "builder": "relation_axis_cards",
    "targetPath": "$.relation_axis_business_customer_cards",
    "axis": {
      "source": "customers",
      "path": "$.customers",
      "nodeType": "customer",
      "idField": "customer_id",
      "titleField": "customer_name"
    },
    "linked": {
      "source": "projects",
      "path": "$.projects",
      "nodeType": "project",
      "idField": "project_id",
      "titleField": "project_name"
    },
    "relation": {
      "source": "relations",
      "path": "$.relations",
      "name": "has_project",
      "direction": "outgoing",
      "includeViaCheck": false
    },
    "diff": {
      "enabled": false
    },
    "outputs": {
      "idField": "customer_id",
      "titleField": "customer_name",
      "linkedItemsField": "related_projects",
      "evidenceEdgesField": "evidence_edges",
      "linkedCountField": "project_count",
      "primaryCountField": "primary_count",
      "secondaryCountField": "secondary_count",
      "coverageField": "coverage"
    },
    "writeBack": {
      "enabled": true,
      "source": "customers",
      "path": "$.customers",
      "keyField": "customer_id",
      "rowKeyField": "customer_id",
      "fields": [
        "customer_name"
      ]
    }
  },
  "views": [
    {
      "id": "relation_axis_business_customer",
      "caption": "relation_axis_business_customer / 顧客軸",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "Business Relation / 基本情報",
          "type": "form",
          "dataPath": "$",
          "fields": [
            {
              "field": "title",
              "caption": "タイトル",
              "type": "text",
              "grid": {
                "visible": false,
                "width": 220
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "schema_version",
              "caption": "Schema",
              "type": "text",
              "grid": {
                "visible": false,
                "width": 120
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "document_type",
              "caption": "Document Type",
              "type": "text",
              "grid": {
                "visible": false,
                "width": 170
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            },
            {
              "field": "note",
              "caption": "メモ",
              "type": "textarea",
              "grid": {
                "visible": false,
                "width": 260
              },
              "edit": {
                "visible": true,
                "readonly": true
              }
            }
          ]
        },
        {
          "id": "main_grid",
          "caption": "relation_axis_business_customer / 顧客軸",
          "type": "grid",
          "dataPath": "$.relation_axis_business_customer_cards",
          "keyField": "customer_id",
          "fields": [
            {
              "field": "customer_id",
              "fieldType": "business.customer_id",
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "readonly": true
              }
            },
            {
              "field": "customer_name",
              "fieldType": "business.customer_name",
              "grid": {
                "visible": true,
                "width": 180
              },
              "edit": {
                "readonly": false
              },
              "readonly": false
            },
            {
              "field": "trace_label",
              "fieldType": "business.trace_label",
              "grid": {
                "visible": true,
                "width": 120
              },
              "edit": {
                "readonly": true
              }
            },
            {
              "field": "project_count",
              "fieldType": "business.project_count",
              "grid": {
                "visible": true,
                "width": 80
              },
              "edit": {
                "readonly": true
              }
            },
            {
              "field": "primary_count",
              "fieldType": "business.primary_count",
              "grid": {
                "visible": true,
                "width": 70
              },
              "edit": {
                "readonly": true
              }
            },
            {
              "field": "secondary_count",
              "fieldType": "business.secondary_count",
              "grid": {
                "visible": true,
                "width": 70
              },
              "edit": {
                "readonly": true
              }
            },
            {
              "field": "coverage",
              "caption": "Coverage",
              "type": "text",
              "grid": {
                "visible": true,
                "width": 110
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "search": {
                "visible": true,
                "operator": "contains"
              }
            },
            {
              "field": "related_projects",
              "caption": "関連案件",
              "type": "objectArray",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "readonly": true
            },
            {
              "field": "evidence_edges",
              "caption": "証跡エッジ",
              "type": "objectArray",
              "grid": {
                "visible": false
              },
              "edit": {
                "visible": true,
                "readonly": true
              },
              "readonly": true
            }
          ]
        }
      ]
    }
  ],
  "fieldTypeSources": [
    "common_types_v0_1.json"
  ]
}
```

</details>