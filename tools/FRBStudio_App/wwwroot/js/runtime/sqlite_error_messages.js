// Presentation-only SQLite error translation. Never parse SQL or SQLite provider messages.
// Receives a stable Data Contract error code + optional table/operation metadata.
(function registerSqliteErrorMessages(global) {
  'use strict';

  const commonMessages = Object.freeze({
    SQLITE_UNIQUE: '同じ値を持つデータがすでに登録されています。重複する項目を確認してください。',
    SQLITE_NOT_NULL: '必須項目が入力されていません。入力内容を確認してください。',
    SQLITE_CHECK: '入力値がデータベースの制約条件を満たしていません。',
    SQLITE_CONSTRAINT: 'データの整合性に関する制約に違反しました。入力内容を確認してください。',
    SQLITE_BUSY: 'データベースがほかの処理で使用中です。少し待ってからやり直してください。',
    SQLITE_READ_ONLY: 'このデータベースは読み取り専用、または書き込み権限がありません。',
    SQLITE_CANNOT_OPEN: 'データベースを開けません。ファイルの場所やアクセス権を確認してください。',
    SQLITE_DISK_FULL: '保存先の空き容量が不足しています。',
    SQLITE_IO_ERROR: 'データベースの読み書きでエラーが発生しました。保存先を確認してください。',
    SQLITE_SAVE_CONFLICT: '読込後に別の処理でデータが変更されました。再読込して内容を確認してください。'
  });

  function toUserMessage(payload) {
    const code = String(payload?.error ?? payload?.code ?? '');
    const details = payload?.details ?? {};
    const operation = String(details.operation ?? '').toUpperCase();
    const table = String(details.table ?? '');
    const context = table ? `テーブル「${table}」：` : '';
    let description;
    if (code === 'SQLITE_FOREIGN_KEY') {
      description = operation === 'DELETE'
        ? '他のデータから参照されているため削除できません。関連データを確認してください。'
        : '関連先のデータが存在しないか、ほかのデータとの参照関係に矛盾があります。';
    } else {
      description = commonMessages[code] ?? 'データベースの保存中にエラーが発生しました。詳しい原因はログで確認してください。';
    }
    return `${context}${description} DBには保存されていません。`;
  }

  global.FRBStudioSqliteErrorMessages = Object.freeze({ toUserMessage });
})(window);
