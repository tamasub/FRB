// v0.5-registry: Field control renderer registry.
// Field type/control selection is centralized here instead of growing createInput branches forever.

const FieldControlRegistry = createNamedRegistry('FieldControlRegistry');

function registerFieldControl(name, factory, aliases=[]) {
  return FieldControlRegistry.register(name, factory, { aliases });
}

function explicitFieldEditorKey(field) {
  const editor = String(field?.editor ?? field?.edit?.editor ?? '').trim();
  if (editor) return editor;

  const control = String(field?.control ?? field?.edit?.control ?? '').trim();
  if (control && !['radio', 'listbox'].includes(control)) return control;
  return '';
}

function fieldControlRegistryKey(field) {
  if (wantsRadioControl(field)) return 'radio';

  // v0.17.6-pluginhost-mvp:
  // type は値の形、editor は触り方。
  // Plugin FieldEditor は type ではなく editor/control の明示指定を優先する。
  const explicitEditor = explicitFieldEditorKey(field);
  if (explicitEditor) return explicitEditor;

  return String(field?.type ?? 'text').trim() || 'text';
}

function createFieldControlElement(context) {
  const field = context.field ?? {};
  const key = fieldControlRegistryKey(field);
  const factory = FieldControlRegistry.get(key) ?? FieldControlRegistry.get('text');
  if (!factory) throw new Error(`FieldControlRegistry: 未登録のfield controlです: ${key}`);
  return factory(context);
}
