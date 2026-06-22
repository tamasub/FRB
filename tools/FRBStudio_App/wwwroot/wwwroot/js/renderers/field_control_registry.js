// v0.5-registry: Field control renderer registry.
// Field type/control selection is centralized here instead of growing createInput branches forever.

const FieldControlRegistry = createNamedRegistry('FieldControlRegistry');

function registerFieldControl(name, factory, aliases=[]) {
  return FieldControlRegistry.register(name, factory, { aliases });
}

function fieldControlRegistryKey(field) {
  if (wantsRadioControl(field)) return 'radio';
  return String(field?.type ?? 'text').trim() || 'text';
}

function createFieldControlElement(context) {
  const field = context.field ?? {};
  const key = fieldControlRegistryKey(field);
  const factory = FieldControlRegistry.get(key) ?? FieldControlRegistry.get('text');
  if (!factory) throw new Error(`FieldControlRegistry: 未登録のfield controlです: ${key}`);
  return factory(context);
}
