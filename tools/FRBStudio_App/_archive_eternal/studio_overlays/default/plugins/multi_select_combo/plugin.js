// Overlay sample plugin: multi_select_combo v0.1.0
// Core PluginHost実装後に有効化する想定。
// ルール: Pluginは会社マスタを内蔵しない。Coreから渡された options を表示するだけ。

(function () {
  window.StudioOverlayPlugins = window.StudioOverlayPlugins || {};
  window.StudioOverlayPlugins.multi_select_combo = {
    id: 'multi_select_combo',
    activate(studio) {
      if (!studio || typeof studio.registerFieldEditor !== 'function') {
        console.info('multi_select_combo: PluginHost is not available yet.');
        return;
      }

      studio.registerFieldEditor('plugin:multi_select_combo', {
        render(context) {
          const select = document.createElement('select');
          select.multiple = true;
          (context.options || []).forEach(opt => {
            const option = document.createElement('option');
            option.value = String(opt.cd ?? opt.value ?? '');
            option.textContent = String(opt.name ?? opt.label ?? option.value);
            select.appendChild(option);
          });
          return select;
        }
      });
    }
  };
})();
