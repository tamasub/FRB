// v0.18.54-combo-option-and-viewdef-maintenance
// Standard select option maintenance. The select itself never decides where to save;
// it follows the source metadata resolved by FieldType / Value Vocabulary / ViewDef.
(function installComboOptionMaintenance(){
  if (window.__studioComboOptionMaintenanceInstalled) return;
  window.__studioComboOptionMaintenanceInstalled = true;

  const runtime = { dialog: null, context: null, selectedIndex: -1 };

  function clone(value) {
    return (typeof cloneData === 'function') ? cloneData(value) : JSON.parse(JSON.stringify(value));
  }

  function sourceLabel(source) {
    if (!source) return '定義元不明';
    if (source.source_type === 'valueVocabulary') return `Value Vocabulary: ${source.ref || ''}`;
    if (source.source_type === 'fieldType') return `共通FieldType: ${source.ref || ''}`;
    if (source.source_type === 'viewDefOptions') return `ViewDef options: ${source.field || ''}`;
    if (source.source_type === 'fixed') return 'System固定候補';
    return source.source_type || source.kind || '定義元不明';
  }

  function resolveSource(field) {
    const explicit = field?._option_maintenance_source ? clone(field._option_maintenance_source) : null;
    if (explicit) {
      if (explicit.kind === 'viewdef') {
        explicit.path = safeJsonFileName(explicit.path || lastLoadedDefName || $('defNameInput')?.value);
        explicit.field = explicit.field || String(field?.field ?? '');
        if (!explicit.path) explicit.readonly = true;
      }
      return explicit;
    }

    if (Array.isArray(field?.options)) {
      const path = safeJsonFileName(lastLoadedDefName || $('defNameInput')?.value);
      return {
        kind: 'viewdef',
        path,
        source_type: 'viewDefOptions',
        field: String(field?.field ?? ''),
        readonly: !path
      };
    }

    if (field?.type === 'boolean') {
      return { kind: 'fixed', source_type: 'fixed', readonly: true, reason: 'booleanのtrue/false候補はStudio Runtime固定です。' };
    }

    return { kind: 'unknown', source_type: 'unknown', readonly: true, reason: '選択肢の正本を一意に特定できません。' };
  }

  function optionValueField(field, source) {
    if (source?.source_type === 'valueVocabulary') return 'cd';
    return field?.valueField ?? field?.value_field ?? field?.optionValueField ?? field?.option_value_field ?? 'cd';
  }

  function optionLabelField(field, source) {
    if (source?.source_type === 'valueVocabulary') return 'name';
    return field?.labelField ?? field?.label_field ?? field?.optionLabelField ?? field?.option_label_field ?? 'name';
  }

  function displayItem(raw, field, source, index) {
    if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
      const vf = optionValueField(field, source);
      const lf = optionLabelField(field, source);
      const value = raw[vf] ?? raw.cd ?? raw.value ?? raw.id ?? '';
      const label = raw[lf] ?? raw.name ?? raw.label ?? raw.caption ?? value;
      return { index, value: String(value ?? ''), label: String(label ?? ''), deprecated: raw.deprecated === true };
    }
    return { index, value: String(raw ?? ''), label: String(raw ?? ''), deprecated: false };
  }

  function nodeAtDefinitionPath(root, definitionPath) {
    const text = String(definitionPath ?? '').trim();
    if (!text || text === '$') return root;
    if (!text.startsWith('$')) return null;
    const tokens = [];
    const re = /\.([A-Za-z0-9_]+)|\[(\d+)\]/g;
    let match;
    let consumed = 1;
    while ((match = re.exec(text)) !== null) {
      if (match.index !== consumed) return null;
      tokens.push(match[1] != null ? match[1] : Number(match[2]));
      consumed = re.lastIndex;
    }
    if (consumed !== text.length) return null;
    let current = root;
    for (const token of tokens) {
      if (current == null || typeof current !== 'object') return null;
      current = current[token];
    }
    return current ?? null;
  }

  function findViewDefOptionsNode(root, fieldName, definitionPath='') {
    const exact = nodeAtDefinitionPath(root, definitionPath);
    if (exact && typeof exact === 'object' && String(exact.field ?? '') === fieldName && Array.isArray(exact.options)) {
      return exact;
    }

    // Backward-compatible fallback for older resolved fields without node_path metadata.
    let best = null;
    const walk = (node) => {
      if (best || node == null) return;
      if (Array.isArray(node)) {
        node.forEach(walk);
        return;
      }
      if (typeof node !== 'object') return;
      if (String(node.field ?? '') === fieldName && Array.isArray(node.options)) {
        best = node;
        return;
      }
      Object.values(node).forEach(walk);
    };
    walk(root);
    return best;
  }

  function findFieldTypeNode(root, ref) {
    const key = String(ref ?? '').trim();
    if (!key) return null;
    const dot = key.indexOf('.');
    const ns = dot > 0 ? key.slice(0, dot) : '';
    const id = dot > 0 ? key.slice(dot + 1) : key;
    const namespaces = root?.namespaces;
    if (Array.isArray(namespaces)) {
      for (const nsObj of namespaces) {
        const nsId = String(nsObj?.namespace_id ?? nsObj?.namespaceId ?? nsObj?.id ?? '').trim();
        if (ns && nsId !== ns) continue;
        const types = nsObj?.fieldTypes ?? nsObj?.field_types;
        if (Array.isArray(types)) {
          const found = types.find(x => String(x?.id ?? x?.field_type_id ?? x?.name ?? '') === id);
          if (found) return found;
        } else if (types?.[id]) return types[id];
      }
    } else if (namespaces && typeof namespaces === 'object') {
      if (ns && (namespaces[ns]?.fieldTypes?.[id] || namespaces[ns]?.field_types?.[id])) {
        return namespaces[ns].fieldTypes?.[id] ?? namespaces[ns].field_types?.[id];
      }
      for (const nsObj of Object.values(namespaces)) {
        if (nsObj?.fieldTypes?.[id]) return nsObj.fieldTypes[id];
        if (nsObj?.field_types?.[id]) return nsObj.field_types[id];
      }
    }
    return root?.fieldTypes?.[id] ?? root?.field_types?.[id] ?? null;
  }

  function findVocabularyNode(root, ref) {
    const key = String(ref ?? '').trim();
    if (!key) return null;
    const dot = key.indexOf('.');
    const ns = dot > 0 ? key.slice(0, dot) : '';
    const id = dot > 0 ? key.slice(dot + 1) : key;
    const namespaces = root?.namespaces;
    if (Array.isArray(namespaces)) {
      for (const nsObj of namespaces) {
        const nsId = String(nsObj?.namespace_id ?? nsObj?.namespaceId ?? nsObj?.id ?? '').trim();
        if (ns && nsId !== ns) continue;
        const enums = nsObj?.enums;
        if (Array.isArray(enums)) {
          const found = enums.find(x => String(x?.enum_ref ?? x?.enumRef ?? '') === key || String(x?.enum_id ?? x?.enumId ?? x?.id ?? '') === id);
          if (found) return found;
        } else if (enums?.[id]) return enums[id];
      }
    } else if (namespaces && typeof namespaces === 'object') {
      if (ns && namespaces[ns]?.enums) {
        const enums = namespaces[ns].enums;
        if (Array.isArray(enums)) {
          const found = enums.find(x => String(x?.enum_ref ?? x?.enumRef ?? '') === key || String(x?.enum_id ?? x?.enumId ?? x?.id ?? '') === id);
          if (found) return found;
        } else if (enums?.[id]) return enums[id];
      }
      for (const nsObj of Object.values(namespaces)) {
        const enums = nsObj?.enums;
        if (Array.isArray(enums)) {
          const found = enums.find(x => String(x?.enum_ref ?? x?.enumRef ?? '') === key || String(x?.enum_id ?? x?.enumId ?? x?.id ?? '') === id);
          if (found) return found;
        } else if (enums?.[id]) return enums[id];
      }
    }
    const rootEnums = root?.enums;
    if (Array.isArray(rootEnums)) return rootEnums.find(x => String(x?.enum_ref ?? x?.enumRef ?? '') === key || String(x?.enum_id ?? x?.enumId ?? x?.id ?? '') === id) ?? null;
    return rootEnums?.[key] ?? rootEnums?.[id] ?? null;
  }

  async function loadContext(field, source) {
    if (source.readonly || !source.path || !['viewdef', 'defs', 'data', 'overlay'].includes(source.kind)) {
      return { field, source, document: null, node: null, draft: clone(field?.options ?? []) };
    }

    let documentJson;
    if (source.kind === 'viewdef' || source.kind === 'defs') documentJson = await fetchApiJson('defs', source.path);
    else documentJson = await fetchApiJson('data', source.path);

    let node = null;
    let rawItems = [];
    if (source.source_type === 'viewDefOptions') {
      node = findViewDefOptionsNode(documentJson, source.field || String(field?.field ?? ''), source.node_path);
      rawItems = node?.options;
    } else if (source.source_type === 'fieldType') {
      node = findFieldTypeNode(documentJson, source.ref);
      rawItems = node?.options;
    } else if (source.source_type === 'valueVocabulary') {
      node = findVocabularyNode(documentJson, source.ref);
      rawItems = node?.items ?? node?.options;
    }

    if (!node || !Array.isArray(rawItems)) {
      return { field, source: { ...source, readonly: true, reason: `定義元は見つかりましたが、選択肢配列を特定できませんでした: ${sourceLabel(source)}` }, document: documentJson, node: null, draft: [] };
    }

    return { field, source, document: documentJson, node, draft: clone(rawItems) };
  }

  function ensureDialog() {
    if (runtime.dialog) return runtime.dialog;
    const dialog = document.createElement('dialog');
    dialog.id = 'comboOptionMaintenanceDialog';
    dialog.className = 'combo-option-maintenance-dialog';
    dialog.innerHTML = `
      <section class="combo-option-maintenance-panel">
        <div class="combo-option-maintenance-title-row">
          <div>
            <div class="app-kicker dark">Combo Options</div>
            <h2>選択肢メンテナンス</h2>
          </div>
          <button type="button" class="icon-button" data-action="close" aria-label="閉じる">×</button>
        </div>
        <div class="combo-option-maintenance-meta" data-role="meta"></div>
        <div class="combo-option-maintenance-table-wrap">
          <table class="combo-option-maintenance-table">
            <thead><tr><th>値</th><th>表示名</th><th>状態</th></tr></thead>
            <tbody data-role="rows"></tbody>
          </table>
        </div>
        <div class="combo-option-maintenance-note" data-role="note"></div>
        <div class="combo-option-maintenance-actions">
          <div>
            <button type="button" class="ghost-button small" data-action="add">追加</button>
            <button type="button" class="ghost-button small" data-action="edit">修正</button>
            <button type="button" class="ghost-button small danger" data-action="delete">削除</button>
          </div>
          <div>
            <button type="button" class="ghost-button small" data-action="close">閉じる</button>
            <button type="button" class="primary-button small" data-action="save">保存</button>
          </div>
        </div>
      </section>`;
    document.body.appendChild(dialog);
    dialog.addEventListener('cancel', e => { e.preventDefault(); dialog.close(); });
    dialog.addEventListener('click', onDialogClick);
    runtime.dialog = dialog;
    return dialog;
  }

  function selectedDraftItem() {
    const ctx = runtime.context;
    if (!ctx || runtime.selectedIndex < 0 || runtime.selectedIndex >= ctx.draft.length) return null;
    return ctx.draft[runtime.selectedIndex];
  }

  function renderDialog() {
    const dialog = ensureDialog();
    const ctx = runtime.context;
    if (!ctx) return;
    const source = ctx.source;
    dialog.querySelector('[data-role="meta"]').textContent = `${ctx.field?.caption ?? ctx.field?.field ?? 'ComboBox'}  /  ${sourceLabel(source)}${source.path ? `  /  ${source.path}` : ''}`;
    const rows = dialog.querySelector('[data-role="rows"]');
    rows.innerHTML = '';
    ctx.draft.forEach((raw, index) => {
      const item = displayItem(raw, ctx.field, source, index);
      const tr = document.createElement('tr');
      tr.dataset.index = String(index);
      if (index === runtime.selectedIndex) tr.classList.add('selected');
      if (item.deprecated) tr.classList.add('deprecated');
      tr.innerHTML = `<td></td><td></td><td></td>`;
      tr.children[0].textContent = item.value;
      tr.children[1].textContent = item.label;
      tr.children[2].textContent = item.deprecated ? '無効' : '有効';
      rows.appendChild(tr);
    });

    const readonly = Boolean(source.readonly || !ctx.node);
    const add = dialog.querySelector('[data-action="add"]');
    const edit = dialog.querySelector('[data-action="edit"]');
    const del = dialog.querySelector('[data-action="delete"]');
    const save = dialog.querySelector('[data-action="save"]');
    add.disabled = readonly;
    edit.disabled = readonly || !selectedDraftItem();
    del.disabled = readonly || !selectedDraftItem();
    save.disabled = readonly;
    const selected = selectedDraftItem();
    const selectedDisplay = selected ? displayItem(selected, ctx.field, source, runtime.selectedIndex) : null;
    del.textContent = source.source_type === 'valueVocabulary' && selectedDisplay?.deprecated ? '有効化' : '削除';
    const policy = source.source_type === 'valueVocabulary' ? '削除は既存Data保護のため deprecated=true（無効化）として保存します。' : '削除は選択肢配列から削除します。';
    dialog.querySelector('[data-role="note"]').textContent = readonly ? (source.reason || 'この選択肢は現在メンテナンス対象外です。') : policy;
  }

  async function promptText(title, message, defaultValue='') {
    if (typeof showStudioPromptDialog !== 'function') return window.prompt(message, defaultValue);
    return showStudioPromptDialog({ title, message, defaultValue, okText: '決定' });
  }

  async function addItem() {
    const ctx = runtime.context;
    if (!ctx || ctx.source.readonly) return;
    const value = await promptText('選択肢を追加', '保存する値を入力してください。', '');
    if (value == null || String(value).trim() === '') return;
    const normalizedValue = String(value).trim();
    if (ctx.draft.some((raw, index) => displayItem(raw, ctx.field, ctx.source, index).value === normalizedValue)) {
      setStatus(`選択肢「${normalizedValue}」は既に存在します`, { kind: 'warn', title: '重複' });
      return;
    }
    const label = await promptText('表示名', '画面に表示する名前を入力してください。', normalizedValue);
    if (label == null) return;

    const sampleObject = ctx.draft.find(x => x && typeof x === 'object' && !Array.isArray(x));
    if (ctx.source.source_type === 'valueVocabulary') {
      const maxOrder = Math.max(0, ...ctx.draft.map(x => Number(x?.sort_order ?? 0)).filter(Number.isFinite));
      ctx.draft.push({ cd: normalizedValue, name: String(label), sort_order: maxOrder + 10, deprecated: false });
    } else if (sampleObject) {
      const vf = optionValueField(ctx.field, ctx.source);
      const lf = optionLabelField(ctx.field, ctx.source);
      const maxOrder = Math.max(0, ...ctx.draft.map(x => Number(x?.sort_order ?? 0)).filter(Number.isFinite));
      const item = { [vf]: normalizedValue, [lf]: String(label) };
      if (ctx.draft.some(x => x && typeof x === 'object' && 'sort_order' in x)) item.sort_order = maxOrder + 10;
      ctx.draft.push(item);
    } else {
      const labelText = String(label);
      if (labelText !== normalizedValue) {
        const vf = optionValueField(ctx.field, ctx.source);
        const lf = optionLabelField(ctx.field, ctx.source);
        ctx.draft.push({ [vf]: normalizedValue, [lf]: labelText });
      } else {
        ctx.draft.push(normalizedValue);
      }
    }
    runtime.selectedIndex = ctx.draft.length - 1;
    renderDialog();
  }

  async function editItem() {
    const ctx = runtime.context;
    const raw = selectedDraftItem();
    if (!ctx || raw == null || ctx.source.readonly) return;
    const current = displayItem(raw, ctx.field, ctx.source, runtime.selectedIndex);
    const value = await promptText('選択肢を修正', '保存する値を修正できます。既存Dataがこの値を使用している場合は変更に注意してください。', current.value);
    if (value == null || String(value).trim() === '') return;
    const normalizedValue = String(value).trim();
    if (ctx.draft.some((item, index) => index !== runtime.selectedIndex && displayItem(item, ctx.field, ctx.source, index).value === normalizedValue)) {
      setStatus(`選択肢「${normalizedValue}」は既に存在します`, { kind: 'warn', title: '重複' });
      return;
    }
    const label = await promptText('表示名を修正', '画面に表示する名前を入力してください。', current.label || normalizedValue);
    if (label == null) return;

    if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
      const vf = optionValueField(ctx.field, ctx.source);
      const lf = optionLabelField(ctx.field, ctx.source);
      raw[vf] = normalizedValue;
      raw[lf] = String(label);
      if (ctx.source.source_type === 'valueVocabulary') raw.deprecated = false;
    } else {
      const labelText = String(label);
      if (labelText !== normalizedValue) {
        const vf = optionValueField(ctx.field, ctx.source);
        const lf = optionLabelField(ctx.field, ctx.source);
        ctx.draft[runtime.selectedIndex] = { [vf]: normalizedValue, [lf]: labelText };
      } else {
        ctx.draft[runtime.selectedIndex] = normalizedValue;
      }
    }
    renderDialog();
  }

  async function deleteItem() {
    const ctx = runtime.context;
    const raw = selectedDraftItem();
    if (!ctx || raw == null || ctx.source.readonly) return;
    const item = displayItem(raw, ctx.field, ctx.source, runtime.selectedIndex);
    if (ctx.source.source_type === 'valueVocabulary') {
      if (raw && typeof raw === 'object' && !Array.isArray(raw)) raw.deprecated = !item.deprecated;
    } else {
      let ok = true;
      if (typeof showStudioConfirmDialog === 'function') {
        ok = await showStudioConfirmDialog({ title: '選択肢を削除', message: `「${item.value} / ${item.label}」を選択肢から削除します。`, danger: true, okText: '削除' });
      }
      if (!ok) return;
      ctx.draft.splice(runtime.selectedIndex, 1);
      runtime.selectedIndex = Math.min(runtime.selectedIndex, ctx.draft.length - 1);
    }
    renderDialog();
  }

  function visibleOptionsFromContext(ctx) {
    if (ctx.source.source_type === 'valueVocabulary') {
      return ctx.draft.filter(x => x?.deprecated !== true).map(clone);
    }
    return ctx.draft.map(clone);
  }

  function applyResolvedOptionsToCurrentView(ctx) {
    const options = visibleOptionsFromContext(ctx);
    const source = ctx.source;
    const targetField = String(ctx.field?.field ?? source.field ?? '');
    const walk = (node) => {
      if (node == null) return;
      if (Array.isArray(node)) { node.forEach(walk); return; }
      if (typeof node !== 'object') return;
      let match = false;
      if (source.source_type === 'valueVocabulary') match = String(node._resolved_value_vocabulary_ref ?? '') === String(source.ref ?? '');
      else if (source.source_type === 'fieldType') match = String(node.fieldType ?? node.field_type ?? '') === String(source.ref ?? '') && !node._resolved_value_vocabulary_ref;
      else if (source.source_type === 'viewDefOptions') match = String(node.field ?? '') === targetField && node?._option_maintenance_source?.source_type === 'viewDefOptions';
      if (match) node.options = clone(options);
      Object.values(node).forEach(walk);
    };
    walk(viewDef);

    if (typeof renderByKey === 'function') {
      renderByKey('header');
      renderByKey('search');
      if (typeof loadRows === 'function') loadRows();
      renderByKey('grid');
    }
    const detailDialog = $('detailDialog');
    if (detailDialog?.open && typeof renderDetailForRow === 'function') {
      const row = detailMode === 'new' ? draftRow : currentRows?.[selectedIndex];
      if (row) renderDetailForRow(row);
    }
  }

  async function saveContext() {
    const ctx = runtime.context;
    if (!ctx || ctx.source.readonly || !ctx.node || !ctx.document) return;
    if (ctx.source.source_type === 'valueVocabulary') ctx.node.items = clone(ctx.draft);
    else ctx.node.options = clone(ctx.draft);

    let url;
    if (ctx.source.kind === 'viewdef' || ctx.source.kind === 'defs') url = apiJsonUrl('defs', ctx.source.path);
    else if (ctx.source.kind === 'data') url = apiJsonUrl('data', ctx.source.path);
    else throw new Error('この定義元は上書き保存できません');

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ctx.document)
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`選択肢の保存に失敗しました (${res.status}) ${text}`);
    }

    if (typeof fieldTypeRegistryCache !== 'undefined') fieldTypeRegistryCache.clear();
    if (typeof enumRegistryCache !== 'undefined') enumRegistryCache.clear();
    if (typeof fieldGroupRegistryCache !== 'undefined') fieldGroupRegistryCache.clear();
    if ((ctx.source.kind === 'viewdef' || ctx.source.kind === 'defs') && typeof invalidateDefinitionTargetViewDefCache === 'function') {
      invalidateDefinitionTargetViewDefCache(ctx.source.path);
    }
    applyResolvedOptionsToCurrentView(ctx);
    setStatus(`選択肢を保存しました: ${sourceLabel(ctx.source)} / ${ctx.source.path}`, { kind: 'success', title: 'Combo更新', toast: false });
    runtime.dialog?.close();
  }

  async function onDialogClick(event) {
    const row = event.target.closest('tbody tr[data-index]');
    if (row) {
      runtime.selectedIndex = Number(row.dataset.index);
      renderDialog();
      return;
    }
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    event.preventDefault();
    const action = button.dataset.action;
    try {
      if (action === 'close') runtime.dialog?.close();
      else if (action === 'add') await addItem();
      else if (action === 'edit') await editItem();
      else if (action === 'delete') await deleteItem();
      else if (action === 'save') await saveContext();
    } catch (err) {
      console.error(err);
      setStatus(`選択肢メンテナンスに失敗しました: ${err.message}`, { kind: 'error', title: 'Comboメンテナンス' });
    }
  }

  async function openForSelect(input, field) {
    const source = resolveSource(field);
    try {
      runtime.context = await loadContext(field, source);
    } catch (err) {
      runtime.context = { field, source: { ...source, readonly: true, reason: err.message }, document: null, node: null, draft: clone(field?.options ?? []) };
    }
    runtime.selectedIndex = runtime.context.draft.length ? 0 : -1;
    renderDialog();
    const dialog = ensureDialog();
    if (!dialog.open) dialog.showModal();
  }

  window.bindComboOptionMaintenance = function bindComboOptionMaintenance(input, field) {
    if (!input || String(input.tagName).toLowerCase() !== 'select') return input;
    input.__studioOptionMaintenanceField = field;
    input.title = input.title || '右クリック: 選択肢メンテナンス';
    if (input.dataset.optionMaintenanceInstalled === '1') return input;
    input.dataset.optionMaintenanceInstalled = '1';
    input.addEventListener('contextmenu', (event) => {
      event.preventDefault();
      event.stopPropagation();
      openForSelect(input, input.__studioOptionMaintenanceField ?? field);
    });
    return input;
  };
})();
