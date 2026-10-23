// studio_work_0268: date precision search options sourced from Studio app_settings.json.
// Keep date storage/Validation unchanged. Explicit configuration is separate from ViewDef.
var StudioSmartSearchDateSettings = (function () {
  'use strict';
  const defaults = Object.freeze({year_mode:'fiscal',fiscal_year_start_month:4});
  let current = defaults;
  function normalize(input) {
    if (!input || typeof input !== 'object') throw new Error('date_search 設定が不正です');
    const year_mode=input.year_mode;
    const fiscal_year_start_month=input.fiscal_year_start_month;
    if (!['fiscal','calendar'].includes(year_mode) || !Number.isInteger(fiscal_year_start_month) || fiscal_year_start_month<1 || fiscal_year_start_month>12) {
      throw new Error('date_search の year_mode は fiscal/calendar、開始月は1〜12を指定してください');
    }
    return Object.freeze({year_mode,fiscal_year_start_month});
  }
  const ready=(async () => {
    try {
      const response = await fetch('config/app_settings.json', {cache:'no-store'});
      if (!response.ok) throw new Error('app_settings.json: '+response.status);
      const data = await response.json();
      current = normalize(data?.smart_search?.date_search ?? defaults);
    } catch (err) {
      console.warn('Smart Search date_search設定を読み込めませんでした。年度始まり4月で続行します。', err);
    }
    return current;
  })();
  return Object.freeze({get:()=>current,ready,normalize});
})();
