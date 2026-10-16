"""Safely add CSV import settings to both FRB Launch ViewDefs.

Run from the tool root after extracting the companion diff ZIP.
Never replaces an existing ViewDef with a bundled/stale copy.
"""
from __future__ import annotations

import copy
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = Path('defs/launch/frb_launch_maintenance_view_def_v0_1.json')

CSV_IMPORT = {
    'enabled': True,
    'caption': 'CSV取込',
    'mode': 'replace_all',
    'columns': {
        'title': ['名前', '氏名', '表示名', '宛先名', 'フルネーム', 'Name', 'Full Name', 'Display Name', 'タイトル'],
        'value': ['値', 'メールアドレス', '電子メールアドレス', '電子メール アドレス', 'Email', 'E-mail',
                  'Email Address', 'E-mail Address', 'E-mail 1 - Value', 'E-mail 2 - Value',
                  'Primary Email', 'メール アドレス'],
        'description': ['説明', '備考', '部署', 'Description'],
    },
    'requiredField': 'value',
    'idField': 'choice_id',
    'idPrefix': 'import_mail_',
    'orderField': 'sort_order',
    'orderStep': 10,
    'maxRows': 10000,
    'defaults': {'group_id': '', 'enabled': True},
    'descriptionFallbackField': 'value',
}


def stage_target(folder: str):
    path = ROOT / folder / TARGET
    if not path.is_file():
        raise FileNotFoundError(f'ViewDef が見つかりません: {path}')
    document = json.loads(path.read_text(encoding='utf-8-sig'))
    views = document.get('views')
    if not isinstance(views, list):
        raise ValueError(f'ViewDef の views が配列ではありません: {path}')
    target = next((item for item in views if item.get('id') == 'launch_choices_view'), None)
    if not target:
        raise ValueError(f'launch_choices_view がありません: {path}')
    sections = target.get('sections', [])
    if not any(section.get('dataPath') == '$.launch_choices' for section in sections):
        raise ValueError(f'対象 DataPath が $.launch_choices ではありません: {path}')
    fields = {field.get('field') for section in sections for field in section.get('fields', [])}
    if not {'title', 'value', 'choice_id', 'group_id'}.issubset(fields):
        raise ValueError(f'候補 Grid の項目構造が予期したものではありません: {path}')
    toolbar = target.setdefault('toolbar', {})
    if not isinstance(toolbar, dict):
        raise ValueError(f'toolbar がObjectではありません: {path}')
    if toolbar.get('csvImport') == CSV_IMPORT:
        return path, None
    toolbar['csvImport'] = copy.deepcopy(CSV_IMPORT)
    return path, document


def main():
    # Validate both files before mutating either one.  Preserves existing
    # ViewDef-specific customizations (presentation, column settings, etc.).
    updates = [stage_target(folder) for folder in ('FRBStudio_App', 'FRB_Launch')]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    for path, document in updates:
        if document is None:
            print(f'[SKIP] 設定済み: {path}')
            continue
        backup = path.with_name(path.name + f'.csvimport_backup_{timestamp}.bak')
        shutil.copy2(path, backup)
        temporary = path.with_name(path.name + '.csvimport_tmp')
        try:
            temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        print(f'[OK] ViewDef拡張: {path}')
        print(f'     変更前のバックアップ: {backup}')
    print('[SUCCESS] 選択候補にCSV取込定義を追加しました。')
    print('Studio NativeShell と FRB Launch をそれぞれ再ビルドしてください。')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'[ERROR] {exc}')
        raise SystemExit(1)
