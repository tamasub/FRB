// Overlay plugin: skill_summary v0.17.6 MVP
// 表示中行に対する集計Actionサンプル。CoreはAction名だけを知り、中身はOverlay側に置く。

(function () {
  function normalizeArray(value) {
    if (Array.isArray(value)) return value;
    if (value == null || value === '') return [];
    return [value];
  }

  function increment(map, key) {
    const k = String(key ?? '').trim();
    if (!k) return;
    map.set(k, (map.get(k) || 0) + 1);
  }

  function topCountsText(map, label) {
    const items = [...map.entries()].sort((a, b) => b[1] - a[1]);
    if (!items.length) return `${label}: なし`;
    return `${label}: ` + items.map(([key, count]) => `${key}=${count}`).join(' / ');
  }

  window.StudioOverlayPlugins = window.StudioOverlayPlugins || {};
  window.StudioOverlayPlugins.skill_summary = {
    id: 'skill_summary',
    activate(studio) {
      studio.registerAction('company.skill_summary.aggregate', async () => {
        const rows = studio.getFilteredRows();
        const qualificationCounts = new Map();
        const skillCounts = new Map();
        const rankCounts = new Map();

        rows.forEach(row => {
          normalizeArray(row?.qualification_cds).forEach(cd => increment(qualificationCounts, cd));
          normalizeArray(row?.attributes).forEach(attr => {
            increment(skillCounts, attr?.skill_cd || attr?.skill_name);
            increment(rankCounts, attr?.rank);
          });
        });

        const lines = [
          `表示中 ${rows.length} 件を集計しました!!!!!`,
          topCountsText(qualificationCounts, '資格'),
          topCountsText(skillCounts, 'スキル'),
          topCountsText(rankCounts, 'ランク')
        ];
        console.table({
          rows: rows.length,
          qualifications: Object.fromEntries(qualificationCounts),
          skills: Object.fromEntries(skillCounts),
          ranks: Object.fromEntries(rankCounts)
        });
        return {
          message: lines.join('\n'),
          statusOptions: { kind: 'success', title: 'Plugin集計' }
        };
      });
    }
  };
})();
