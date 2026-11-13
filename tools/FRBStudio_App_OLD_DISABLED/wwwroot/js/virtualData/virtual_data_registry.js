// v0.5-registry: virtualData builder registry.
// ViewDefの builder/type/kind 識別子を、固定分岐ではなく登録済みbuilderへ委譲する。

const VirtualDataBuilderRegistry = createNamedRegistry('VirtualDataBuilderRegistry');

function virtualDataBuilderName(config) {
  return String(config?.builder ?? config?.type ?? config?.kind ?? 'relation_axis_cards').trim() || 'relation_axis_cards';
}

function registerVirtualDataBuilder(name, builder, aliases=[]) {
  return VirtualDataBuilderRegistry.register(name, builder, { aliases });
}

function buildVirtualDatasetByConfig({ config, dataObj, sources }) {
  const builderName = virtualDataBuilderName(config);
  const builder = VirtualDataBuilderRegistry.get(builderName);
  if (!builder) throw new Error(`未対応の virtualData builder です: ${builderName}`);
  return builder({ config, dataObj, sources });
}
