// v0.18.35.3-studio-json-round-trip-all-screen-editable-fields
// Studio JSON Round Trip:
// - Copy JSON: current detail editor values (including child subgrids) -> clipboard
// - Paste JSON: clipboard / manual JSON -> current detail editor
// - Paste is draft-only. The existing Apply(F12) remains the commit boundary.
(function installStudioJsonRoundTripRuntime(){
  if (window.__studioJsonRoundTripRuntimeInstalled) return;
  window.__studioJsonRoundTripRuntimeInstalled = true;

  let lastChangedPaths = [];
  let pendingDraftRow = null;
  let pendingTarget = null;

  function currentTarget(){
    if (detailMode === 'new') return { mode: 'new', index: -1, row: draftRow };
    if (selectedIndex >= 0 && Array.isArray(currentRows)) {
      return { mode: 'edit', index: selectedIndex, row: currentRows[selectedIndex] };
    }
    return null;
  }

  function pendingMatchesCurrentTarget(){
    if (!pendingDraftRow || !pendingTarget) return false;
    const target = currentTarget();
    if (!target || target.mode !== pendingTarget.mode) return false;
    if (target.mode === 'new') return target.row === pendingTarget.row;
    return target.index === pendingTarget.index && target.row === pendingTarget.row;
  }

  function currentRow(){
    if (pendingMatchesCurrentTarget()) return pendingDraftRow;
    return currentTarget()?.row ?? null;
  }

  function setPendingDraft(row){
    const target = currentTarget();
    if (!target) throw new Error('詳細エディターの対象行がありません');
    pendingDraftRow = row;
    pendingTarget = target;
  }

  function getPendingDraftRow(){
    return pendingMatchesCurrentTarget() ? pendingDraftRow : null;
  }

  function consumePendingDraft(){
    if (!pendingMatchesCurrentTarget()) return null;
    // F12/前後移動の時点で、通常入力・サブグリッドの最新UI値をDraftへ回収する。
    if (typeof applyDetailInputsToRow === 'function') applyDetailInputsToRow(pendingDraftRow);
    const committed = cloneData(pendingDraftRow);
    pendingDraftRow = null;
    pendingTarget = null;
    clearRoundTripDiff();
    return committed;
  }

  function discardPendingDraft(){
    pendingDraftRow = null;
    pendingTarget = null;
    clearRoundTripDiff();
  }

  function hasByPath(obj, path){
    if (!obj || typeof obj !== 'object') return false;
    const normalized = String(path ?? '').replace(/^\$\.?/, '');
    if (!normalized) return true;
    const parts = normalized.split('.');
    let cur = obj;
    for (const part of parts) {
      if (cur == null || typeof cur !== 'object' || !Object.prototype.hasOwnProperty.call(cur, part)) return false;
      cur = cur[part];
    }
    return true;
  }

  function sameJsonValue(a, b){
    if (a === b) return true;
    try { return JSON.stringify(a) === JSON.stringify(b); }
    catch { return false; }
  }

  function addContract(map, path, config={}){
    const name = String(path ?? '').trim();
    if (!name || name.startsWith('__')) return;
    const existing = map.get(name);
    const next = {
      path: name,
      type: config.type ?? existing?.type ?? 'text',
      editable: Boolean(config.editable ?? existing?.editable),
      field: config.field ?? existing?.field ?? null,
      source: config.source ?? existing?.source ?? 'field'
    };
    // 同じ実データ項目が通常欄とChat欄の両方に現れる場合、どちらかが編集可なら編集可。
    if (existing?.editable || config.editable) next.editable = true;
    map.set(name, next);
  }

  function chatInputSourceField(field, gd){
    const raw = field?.edit?.input ?? field?.input ?? field?.chat?.input;
    const cfg = raw ?? {};
    const fields = gd?.fields ?? [];
    const existing = new Set(fields.map(item => item?.field).filter(Boolean));
    const hasExplicitInput = raw && typeof raw === 'object';
    const userField = cfg.userField ?? cfg.user_field ?? (!hasExplicitInput && existing.has('user_reply') ? 'user_reply' : null);
    return cfg.enabled === false ? null : userField;
  }

  function contractsForGrid(gd, row=null){
    const map = new Map();
    const fields = gd?.fields ?? [];
    const fieldByName = new Map(fields.map(field => [field.field, field]));

    fields.forEach(field => {
      if (!field?.field) return;
      if (row && typeof fieldMatchesVisibleWhen === 'function' && !fieldMatchesVisibleWhen(field, row)) return;
      const readonly = Boolean(field.readonly || field.edit?.readonly);
      const arrayField = field.type === 'objectArray' || field.type === 'stringArray';

      // objectArray / stringArray は edit.visible=false でも、Detail下部の共通サブグリッド、
      // または対象文脈の専用Gridとして画面入力できる。画面描画契約に合わせて先に登録する。
      if (arrayField) {
        const editable = typeof isDetailSubGridEditable === 'function'
          ? isDetailSubGridEditable(field)
          : !readonly;
        const targetContext = typeof isTargetContextField === 'function' && isTargetContextField(field);
        addContract(map, field.field, {
          type: field.type,
          editable,
          field,
          source: targetContext ? 'target-context' : 'subgrid'
        });
        return;
      }

      if (field.type === 'chat') {
        const messages = field.edit?.messages ?? field.messages ?? field.chat?.messages ?? [];
        (Array.isArray(messages) ? messages : []).forEach(message => {
          const sourceField = fieldByName.get(message?.field) ?? {};
          addContract(map, message?.field, {
            type: sourceField.type ?? message?.type ?? 'textarea',
            editable: !(message?.readonly || sourceField.readonly || sourceField.edit?.readonly),
            field: sourceField,
            source: 'chat-message'
          });
          const embedded = message?.embeddedFields ?? message?.embedded_fields ?? [];
          (Array.isArray(embedded) ? embedded : []).forEach(item => {
            const embeddedSource = fieldByName.get(item?.field) ?? {};
            addContract(map, item?.field, {
              type: embeddedSource.type ?? item?.type ?? 'text',
              editable: !(item?.readonly || item?.edit?.readonly || embeddedSource.readonly || embeddedSource.edit?.readonly),
              field: embeddedSource,
              source: 'chat-embedded'
            });
          });
        });

        // chat composerはmessagesとは別UIだが、userFieldへ人間が入力できる。
        const inputFieldName = chatInputSourceField(field, gd);
        if (inputFieldName) {
          const inputSource = fieldByName.get(inputFieldName) ?? {};
          addContract(map, inputFieldName, {
            type: inputSource.type ?? 'textarea',
            editable: !(inputSource.readonly || inputSource.edit?.readonly),
            field: inputSource,
            source: 'chat-input'
          });
        }
        return;
      }

      // edit.visible=false の通常項目は、Chat等の別UIに出た場合だけ上の契約で追加する。
      if (field.edit?.visible === false) return;
      addContract(map, field.field, {
        type: field.type ?? 'text',
        editable: !readonly,
        field,
        source: 'field'
      });
    });

    return [...map.values()];
  }

  function emptyValueForContract(contract){
    if (contract.type === 'objectArray' || contract.type === 'stringArray' || contract.type === 'array') return [];
    const field = contract.field ?? {};
    if (field.defaultValue !== undefined) return cloneData(field.defaultValue);
    if (field.default_value !== undefined) return cloneData(field.default_value);
    return null;
  }

  function collectEditorRow(){
    const base = currentRow();
    if (!base) throw new Error('詳細エディターの行がありません');
    const working = cloneData(base) ?? {};

    // applyDetailInputsToRowはサブグリッド値の回収時に「反映済み」表示へ更新する。
    // Round TripのCopy/Paste準備は確定操作ではないため、見た目の編集状態を復元する。
    const cards = [...(($('detailDialog') ?? document).querySelectorAll?.('.detail-subgrid-edit') ?? [])];
    const cardStates = cards.map(card => ({
      card,
      className: card.className,
      badge: card.querySelector('.detail-subgrid-dirty-badge'),
      badgeText: card.querySelector('.detail-subgrid-dirty-badge')?.textContent ?? ''
    }));
    try {
      if (typeof applyDetailInputsToRow === 'function') applyDetailInputsToRow(working);
    } finally {
      cardStates.forEach(state => {
        state.card.className = state.className;
        if (state.badge) state.badge.textContent = state.badgeText;
      });
    }
    return working;
  }

  function buildRoundTripJson(){
    const gd = gridDef();
    if (!gd) throw new Error('Grid ViewDefが読み込まれていません');
    const row = collectEditorRow();
    const output = {};
    contractsForGrid(gd, row).forEach(contract => {
      const value = hasByPath(row, contract.path)
        ? cloneData(getByPath(row, contract.path))
        : emptyValueForContract(contract);
      setByPath(output, contract.path, value);
    });
    return output;
  }

  function normalizeJsonText(text){
    let value = String(text ?? '').trim();
    const fenced = value.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
    if (fenced) value = fenced[1].trim();
    return value.replace(/^\uFEFF/, '');
  }

  function parseRoundTripJson(text){
    const normalized = normalizeJsonText(text);
    if (!normalized) throw new Error('貼り付けるJSONが空です');
    let parsed;
    try { parsed = JSON.parse(normalized); }
    catch (error) { throw new Error(`JSONを解析できません: ${error.message}`); }
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error('Row JSONはオブジェクト形式で指定してください');
    }
    return parsed;
  }

  function optionContractValue(option, field){
    if (typeof optionValue === 'function') return optionValue(option, field);
    if (option && typeof option === 'object') {
      return option.value ?? option.id ?? option.key ?? option.label ?? option.caption ?? '';
    }
    return option;
  }

  function allowedOptionValues(contract){
    const field = contract.field ?? {};
    const options = Array.isArray(field.options) ? field.options : [];
    return options.map(option => optionContractValue(option, field));
  }

  function validateContractValue(contract, value){
    if (value == null) return null;
    const allowed = allowedOptionValues(contract);
    if (allowed.length && (contract.type === 'select' || contract.field?.edit?.control === 'radio')) {
      const values = Array.isArray(value) ? value : [value];
      const invalid = values.find(item => item !== '' && !allowed.some(option => sameJsonValue(option, item)));
      if (invalid !== undefined) {
        return `${contract.path}: ${JSON.stringify(invalid)} は許可された選択肢ではありません（${allowed.join(' / ')}）`;
      }
    }
    if ((contract.type === 'objectArray' || contract.type === 'stringArray' || contract.type === 'array') && !Array.isArray(value)) {
      return `${contract.path}: 配列を指定してください`;
    }
    if (contract.type === 'objectArray') {
      const invalidIndex = value.findIndex(item => !item || typeof item !== 'object' || Array.isArray(item));
      if (invalidIndex >= 0) return `${contract.path}[${invalidIndex}]: オブジェクトを指定してください`;

      // サブグリッド内のselect/radio等も、親ViewDefのsubGrid.columns契約で検証する。
      // 配列であることだけ確認して通すと、候補外値が画面上で空欄化してしまうため。
      const subGrid = contract.field?.edit?.subGrid
        ?? contract.field?.edit?.subgrid
        ?? contract.field?.edit?.sub_grid
        ?? {};
      const columns = Array.isArray(subGrid.columns) ? subGrid.columns : [];
      for (let itemIndex = 0; itemIndex < value.length; itemIndex++) {
        const item = value[itemIndex];
        for (const column of columns) {
          if (!column?.field || !Object.prototype.hasOwnProperty.call(item, column.field)) continue;
          const childContract = {
            path: `${contract.path}[${itemIndex}].${column.field}`,
            type: column.type ?? 'text',
            editable: true,
            field: column,
            source: 'subgrid-column'
          };
          const childError = validateContractValue(childContract, item[column.field]);
          if (childError) return childError;
        }
      }
    }
    if (contract.type === 'stringArray') {
      const invalidIndex = value.findIndex(item => typeof item !== 'string');
      if (invalidIndex >= 0) return `${contract.path}[${invalidIndex}]: 文字列を指定してください`;
    }
    return null;
  }

  function applyRoundTripObject(payload){
    const gd = gridDef();
    if (!gd) throw new Error('Grid ViewDefが読み込まれていません');
    const working = collectEditorRow();
    const contracts = contractsForGrid(gd, working);
    const errors = [];
    const changes = [];
    const readonlyPaths = [];

    contracts.forEach(contract => {
      if (!hasByPath(payload, contract.path)) return;
      if (!contract.editable) {
        readonlyPaths.push(contract.path);
        return;
      }
      const nextValue = cloneData(getByPath(payload, contract.path));
      const error = validateContractValue(contract, nextValue);
      if (error) {
        errors.push(error);
        return;
      }
      const previousValue = getByPath(working, contract.path);
      if (!sameJsonValue(previousValue, nextValue)) changes.push(contract.path);
      setByPath(working, contract.path, nextValue);
    });

    if (errors.length) throw new Error(errors.join('\n'));
    if (!changes.length) {
      clearRoundTripDiff();
      const readonlyMessage = readonlyPaths.length ? `（読取専用 ${readonlyPaths.length}項目は無視）` : '';
      setStatus(`Paste JSON: 変更はありません${readonlyMessage}`, { toast: false });
      return { changes, readonlyPaths };
    }

    // 画面上のDraftだけを書き換える。実データはまだ変更せず、既存の反映(F12)を確定境界とする。
    // Markdownプレビュー型chatはcontenteditable=falseのため、DOMだけではF12時に値を回収できない。
    // workingは「貼り付け時点の固定スナップショット」ではなく、F12まで編集を続ける作業行。
    // F12時にapplyDetailInputsToRow()で通常項目・サブグリッドの最新UI値を再回収してから確定する。
    setPendingDraft(working);
    renderDetailForRow(working);
    lastChangedPaths = changes;
    highlightRoundTripChanges(changes);
    updateRoundTripDiffBadge(changes, readonlyPaths);
    const readonlyMessage = readonlyPaths.length ? ` / 読取専用 ${readonlyPaths.length}項目は無視` : '';
    setStatus(`Paste JSONを画面へ展開しました: ${changes.length}項目${readonlyMessage}（貼り付け後の手修正も含めてF12で反映）`);
    return { changes, readonlyPaths };
  }

  function cssEscape(value){
    if (window.CSS?.escape) return CSS.escape(String(value));
    return String(value).replace(/["\\]/g, '\\$&');
  }

  function highlightRoundTripChanges(paths){
    const root = $('detailDialog');
    if (!root) return;
    root.querySelectorAll('.studio-json-roundtrip-changed').forEach(el => el.classList.remove('studio-json-roundtrip-changed'));
    paths.forEach(path => {
      root.querySelectorAll(`[data-field="${cssEscape(path)}"]`).forEach(control => {
        const target = control.closest('.field, .chat-message, .chat-embedded-field') ?? control;
        target.classList.add('studio-json-roundtrip-changed');
      });
      const card = root.querySelector(`.detail-subgrid-edit[data-subgrid-field="${cssEscape(path)}"]`);
      if (card) card.classList.add('studio-json-roundtrip-changed');
      const contract = contractsForGrid(gridDef(), currentRow()).find(item => item.path === path);
      if (contract?.source === 'target-context') {
        root.querySelector('#targetContextDetailPanel')?.classList.add('studio-json-roundtrip-changed');
      }
    });
  }

  function updateRoundTripDiffBadge(paths=[], readonlyPaths=[]){
    const badge = $('studioJsonRoundTripDiff');
    if (!badge) return;
    if (!paths.length) {
      badge.textContent = '';
      badge.classList.add('hidden');
      badge.removeAttribute('title');
      return;
    }
    badge.textContent = `JSON差分 ${paths.length}件`;
    badge.title = [
      ...paths.map(path => `変更: ${path}`),
      ...readonlyPaths.map(path => `読取専用のため無視: ${path}`)
    ].join('\n');
    badge.classList.remove('hidden');
  }

  function clearRoundTripDiff(){
    lastChangedPaths = [];
    const root = $('detailDialog');
    root?.querySelectorAll('.studio-json-roundtrip-changed').forEach(el => el.classList.remove('studio-json-roundtrip-changed'));
    updateRoundTripDiffBadge([]);
  }

  async function copyRoundTripJson(){
    try {
      const json = JSON.stringify(buildRoundTripJson(), null, 2);
      if (typeof copyPromptTextToClipboard === 'function') {
        const result = await copyPromptTextToClipboard(json);
        setStatus(result?.fallback ? 'Copy JSON: 手動コピー画面を開きました' : 'Copy JSON: 現在のRow JSONをコピーしました');
        return;
      }
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(json);
        setStatus('Copy JSON: 現在のRow JSONをコピーしました');
        return;
      }
      await showStudioManualCopyDialog?.('Copy JSON', json);
    } catch (error) {
      console.error(error);
      setStatus(`Copy JSONエラー: ${error.message}`, { kind: 'error', title: 'Studio JSON Round Trip' });
    }
  }

  async function readPasteJsonText(){
    if (navigator.clipboard?.readText) {
      try {
        const text = await navigator.clipboard.readText();
        if (String(text ?? '').trim()) return text;
      } catch (error) {
        console.warn('navigator.clipboard.readText failed:', error);
      }
    }
    if (typeof showStudioPromptDialog !== 'function') throw new Error('クリップボードを読み取れませんでした');
    return await showStudioPromptDialog({
      title: 'Paste JSON',
      message: 'AIなどから返されたRow JSONを貼り付けてください。部分JSONにも対応しています。',
      detail: 'JSONに存在する編集可能項目だけを画面へ展開します。サブグリッド配列は配列全体を置き換えます。貼り付け後も通常どおり修正でき、その最新内容を反映(F12)で確定します。',
      defaultValue: '',
      multiline: true,
      okText: '画面へ展開',
      cancelText: 'キャンセル'
    });
  }

  async function pasteRoundTripJson(){
    try {
      const text = await readPasteJsonText();
      if (text == null) return;
      const payload = parseRoundTripJson(text);
      applyRoundTripObject(payload);
    } catch (error) {
      console.error(error);
      setStatus(`Paste JSONエラー: ${error.message}`, { kind: 'error', title: 'Studio JSON Round Trip' });
      if (typeof showStudioConfirmDialog === 'function') {
        await showStudioConfirmDialog({
          title: 'Paste JSONを反映できません',
          message: error.message,
          okText: '閉じる',
          cancelText: '戻る',
          danger: true
        });
      }
    }
  }

  function setup(){
    const copyButton = $('copyDetailJsonBtn');
    const pasteButton = $('pasteDetailJsonBtn');
    if (copyButton && !copyButton.dataset.roundTripBound) {
      copyButton.dataset.roundTripBound = 'true';
      copyButton.addEventListener('click', copyRoundTripJson);
    }
    if (pasteButton && !pasteButton.dataset.roundTripBound) {
      pasteButton.dataset.roundTripBound = 'true';
      pasteButton.addEventListener('click', pasteRoundTripJson);
    }
    const applyButton = $('applyDetailBtn');
    if (applyButton && !applyButton.dataset.roundTripClearBound) {
      applyButton.dataset.roundTripClearBound = 'true';
      applyButton.addEventListener('click', () => window.setTimeout(clearRoundTripDiff, 0));
    }
    const detailDialog = $('detailDialog');
    if (detailDialog && !detailDialog.dataset.roundTripCloseBound) {
      detailDialog.dataset.roundTripCloseBound = 'true';
      detailDialog.addEventListener('close', discardPendingDraft);
    }
  }

  window.setupStudioJsonRoundTrip = setup;
  window.copyStudioDetailJson = copyRoundTripJson;
  window.pasteStudioDetailJson = pasteRoundTripJson;
  window.buildStudioDetailRoundTripJson = buildRoundTripJson;
  window.applyStudioDetailRoundTripObject = applyRoundTripObject;
  window.getStudioJsonRoundTripDraftRow = getPendingDraftRow;
  window.consumeStudioJsonRoundTripDraft = consumePendingDraft;
  window.discardStudioJsonRoundTripDraft = discardPendingDraft;
  window.clearStudioJsonRoundTripDiff = clearRoundTripDiff;
})();
