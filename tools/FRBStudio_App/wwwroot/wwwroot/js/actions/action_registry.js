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
    setStatus,
    renderByKey,
    ...extra
  };
}

// 既存ボタンと同等の代表Actionを登録しておく。
// v0.6では toolbar.executeButton.action から渡された actionId で実行される。
registerStudioAction('LoadData', async () => loadFromFiles(), ['LoadJson']);
registerStudioAction('SaveData', async () => saveOverwriteJson(), ['SaveJson']);
registerStudioAction('ExportMarkdown', async () => {
  await exportMarkdown();
  return { message: 'Markdown出力を実行しました' };
});
registerStudioAction('ExportViewDefMarkdown', async () => {
  await exportViewDefMarkdown();
  return { message: 'ViewDef Markdown出力を実行しました' };
});
registerStudioAction('RefreshServerLists', async () => {
  await refreshServerLists();
  return { message: 'サーバー側JSON一覧を更新しました' };
});
registerStudioAction('ShowActionContext', async (context={}) => {
  console.log('ShowActionContext', context);
  return { message: `ActionContext確認: ${context.executeButton?.action ?? ''}` };
});
registerStudioAction('Noop', async (context={}) => {
  return { message: `${context.executeButton?.caption ?? 'Action'} はNoopとして実行されました` };
});
