// v0.5-registry: Action registry skeleton.
// v0.6-action-execute-button で toolbar.executeButton から actionId を渡すための受け皿。
// この段階では既存ヘッダーボタンの動作は変更しない。

const ActionRegistry = createNamedRegistry('ActionRegistry');

function registerStudioAction(actionId, handler, aliases=[]) {
  return ActionRegistry.register(actionId, handler, { aliases });
}

async function executeStudioAction(actionId, context={}) {
  const action = ActionRegistry.get(actionId);
  if (!action) throw new Error(`未登録のActionです: ${actionId}`);
  return await action(context);
}

function currentStudioActionContext(extra={}) {
  return {
    viewDef,
    sourceData,
    currentRows,
    filteredRows,
    selectedIndex,
    currentDataApiUrl,
    ...extra
  };
}

// 既存ボタンと同等の代表Actionを登録しておく。
// ただしv0.5ではUIからは直接呼ばない。v0.6でViewDef駆動のexecuteButtonに接続する。
registerStudioAction('LoadData', async () => loadFromFiles());
registerStudioAction('SaveData', async () => saveOverwriteJson());
registerStudioAction('ExportMarkdown', async () => exportMarkdown());
registerStudioAction('ExportViewDefMarkdown', async () => exportViewDefMarkdown());
registerStudioAction('RefreshServerLists', async () => refreshServerLists());
