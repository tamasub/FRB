// v0.5-registry: Markdown export registry.
// markdown.type は登録済みbuilderへ委譲し、出力種別追加時の分岐肥大化を防ぐ。

const MarkdownExportRegistry = createNamedRegistry('MarkdownExportRegistry');

function registerMarkdownExportBuilder(name, builder, aliases=[]) {
  return MarkdownExportRegistry.register(name, builder, { aliases });
}

function buildMarkdownByRegisteredType(type) {
  const key = String(type ?? '').trim() || 'auto';
  const builder = MarkdownExportRegistry.get(key) ?? MarkdownExportRegistry.get('auto');
  if (!builder) throw new Error(`未対応の markdown export type です: ${key}`);
  return builder();
}
