// Overlay plugin: multi_select_combo v0.17.6 MVP
// ルール: Pluginは会社マスタを内蔵しない。Coreから渡された field.options を表示するだけ。

(function () {
  function normalizeArray(value) {
    if (Array.isArray(value)) return value;
    if (value == null || value === '') return [];
    return String(value).split(',').map(x => x.trim()).filter(Boolean);
  }

  function isMultiSelectField(field) {
    const editor = String(field?.editor ?? field?.edit?.editor ?? '').trim();
    return editor === 'plugin:multi_select_combo' || editor === 'multi_select_combo';
  }

  function optionValue(opt, studio, field) {
    return String(studio.optionValue ? studio.optionValue(opt, field) : (opt?.cd ?? opt?.value ?? opt ?? ''));
  }

  function optionLabel(opt, studio, field) {
    return String(studio.optionLabel ? studio.optionLabel(opt, field) : (opt?.name ?? opt?.label ?? opt?.cd ?? opt?.value ?? opt ?? ''));
  }

  function createMultiSelect(field, value, studio, onChange) {
    const select = document.createElement('select');
    select.multiple = true;
    select.className = 'studio-plugin-multi-select';
    select.dataset.valueMode = 'array';

    // ★ 動作確認用：Pluginで描画されていることを目視確認する
    select.style.fontSize = '22px';
    select.style.minHeight = '110px';
    select.title = 'multi_select_combo plugin is active';
    select.dataset.pluginActive = 'multi_select_combo_v0_17_6';

    const selected = new Set(normalizeArray(value).map(String));
    (field.options || []).forEach(opt => {
      const option = document.createElement('option');
      option.value = optionValue(opt, studio, field);
      option.textContent = `🔌 ${optionLabel(opt, studio, field)}`;
      option.selected = selected.has(String(option.value));
      select.appendChild(option);
    });
    

    if (typeof onChange === 'function') {
      select.addEventListener('change', () => onChange([...select.selectedOptions].map(opt => opt.value)));
    }
    return select;
  }

  window.StudioOverlayPlugins = window.StudioOverlayPlugins || {};
  window.StudioOverlayPlugins.multi_select_combo = {
    id: 'multi_select_combo',
    activate(studio) {
      studio.registerFieldEditor('plugin:multi_select_combo', {
        render(context) {
          const field = context.field || {};
          return createMultiSelect(field, context.value, studio);
        }
      }, ['multi_select_combo']);

      studio.registerSearchFilter('company.multi_select_combo.search', {
        caption: '複数選択検索',
        visible(context) {
          return (context.gd?.fields || []).some(field => isMultiSelectField(field) && field.search?.pluginFilter === true);
        },
        render(host, context) {
          const fields = (context.gd?.fields || []).filter(field => isMultiSelectField(field) && field.search?.pluginFilter === true);
          fields.forEach(field => {
            const label = document.createElement('label');
            label.textContent = field.search?.caption ?? `${field.caption ?? field.field} 検索`;
            host.appendChild(label);

            const currentValue = context.state[field.field] || [];
            const select = createMultiSelect(field, currentValue, studio, selected => {
              context.state[field.field] = selected;
            });
            select.dataset.pluginSearchField = field.field;
            host.appendChild(select);

            const hint = document.createElement('div');
            hint.className = 'studio-plugin-field-hint';
            hint.textContent = 'いずれかを含む行を表示します。未選択なら条件なし。';
            host.appendChild(hint);
          });
        },
        predicate(row, state, context) {
          const fields = (context.gd?.fields || []).filter(field => isMultiSelectField(field) && field.search?.pluginFilter === true);
          return fields.every(field => {
            const selected = normalizeArray(state[field.field]).map(String);
            if (!selected.length) return true;
            const rowValues = normalizeArray(studio.getByPath(row, field.field)).map(String);
            const match = String(field.search?.match ?? 'includesAny');
            if (match === 'includesAll') return selected.every(value => rowValues.includes(value));
            return selected.some(value => rowValues.includes(value));
          });
        },
        reset(state) {
          Object.keys(state).forEach(key => { state[key] = []; });
        }
      });
    }
  };
})();
