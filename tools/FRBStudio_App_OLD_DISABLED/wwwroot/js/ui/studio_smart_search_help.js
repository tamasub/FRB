// studio_work_0268: Small, non-editing hover/focus help for the Smart Search grammar.
// Keep the help as Markdown; use the existing Studio Markdown renderer.
var StudioSmartSearchHelp = (function () {
  'use strict';

  const markdown = [
    '### まずは検索の基本',
    '',
    '| 入力例 | 意味 |',
    '| --- | --- |',
    '| `ルアー 振動` | **AND**：両方を含む（空白区切り） |',
    '| `ルアー or 振動` | **OR**：どちらかを含む（`OR` も可） |',
    '| `タイトル=Studio` | **項目指定**：タイトルに `Studio` を含む |',
    '| `タイトル==Studio` | **完全一致**：タイトルが `Studio` と一致 |',
    '| `種別!=bug` | **不一致**：種別が `bug` 以外 |',
    '| `"重要 案件"` | 空白を含む検索語をひとまとめにする |',
    '',
    '### 比較演算子（書く順番は自由）',
    '',
    '| 入力① | 入力② | 意味 |',
    '| --- | --- | --- |',
    '| `A=2` | ― | 標準検索（数値・選択肢は一致、文字列は部分一致） |',
    '| `A==2` | ― | 完全一致 |',
    '| `A!=2` | `A=!2` | 不一致 |',
    '| `A>=2` | `A=>2` | 2以上 |',
    '| `A<=2` | `A=<2` | 2以下 |',
    '| `A>2` | ― | 2より大きい |',
    '| `A<2` | ― | 2より小さい |',
    '| `A=2..5` | ― | 2以上5以下（両端を含む） |',
    '| `A=2..` | `A=..5` | 開始または終了だけを指定 |',
    '',
    '※ 大小比較・範囲指定は数値や日付の項目で利用します。',
    '',
    '### 日付・日時（入力の長さで期間を指定）',
    '',
    '| 検索式の例 | 検索対象 |',
    '| --- | --- |',
    '| `日付=2026` | 2026年度または2026年（設定で切替） |',
    '| `日付=202610` | 2026年10月の全日 |',
    '| `日付=20261023` | 2026年10月23日 |',
    '| `日時=20261023_15` | 10月23日の15時台 |',
    '| `日時=20261023_1530` | 同日15時30分台 |',
    '| `日時=20261023_153045` | 同日15時30分45秒台 |',
    '| `日時=202610..202611` | 10月1日〜11月30日の全時刻 |',
    '| `日時=20261023_09..20261023_17` | 9時台〜17時台（18時より前） |',
    '',
    '※ 入力の `..` は**終了側の期間も含みます**。年度・暦年の切替は `app_settings.json` の `smart_search.date_search` で設定。',
    '',
    '※ `YYYY-MM-DD` や `YYYY/MM/DD`、時刻付きの従来表記も使えます（`/` キーは補完を開くため貼り付けで入力）。',
    '',

    '',
    '### AND・OR・括弧の組み合わせ',
    '',
    '| 検索式 | 意味 |',
    '| --- | --- |',
    '| `aaa or bbb` | `aaa` または `bbb` |',
    '| `(aaa or bbb) ccc` | ORグループ **AND** `ccc` |',
    '| `((aaa or bbb) or (ccc or ddd))` | ORグループ同士のOR |',
    '| `(aaa or bbb) (ccc or ddd)` | ORグループ同士のAND |',
    '| `((aaa or bbb) ccc) or (ddd eee)` | ANDとORを括弧で組み合わせ |',
    '',
    '※ 優先順位は **括弧 → AND → OR**。括弧は何段でも入れ子にできます。',
    '',
    '### 項目名・入力補完',
    '',
    '| 操作・入力例 | 動作 |',
    '| --- | --- |',
    '| `"Flux A">=0.1` | 空白を含む項目名は引用符で囲む |',
    '| `/` または検索欄の右クリック | 項目候補を表示（`/` は入力文字に残らない） |',
    '| `↑` / `↓` | 候補を移動 |',
    '| `Tab` / `Enter` / `→` | 候補を確定。選択肢がある項目は値候補へ |',
    '| `Esc` | 候補を閉じる |',
    '| 候補一覧の検索欄 | 項目・選択値を絞り込む |',
    '',
    '※ 項目名は表示名でも項目IDでも指定できます。',
  ].join('\n');

  function setup(args={}) {
    const holder=args.holder, button=args.button, tooltip=args.tooltip, section=args.section;
    if (!holder || !button || !tooltip || !section) return null;
    if (typeof renderMarkdownContent === 'function') {
      tooltip.innerHTML=renderMarkdownContent(markdown,{enabled:true});
    } else {
      // A safe, legible fallback if the host does not ship Studio's Markdown renderer.
      tooltip.textContent=markdown;
    }
    let opened=false;
    let closeTimer=null;
    function cancelPendingClose() {
      if (closeTimer === null) return;
      clearTimeout(closeTimer);
      closeTimer=null;
    }
    function open() {
      cancelPendingClose();
      if (opened) return;
      opened=true;
      tooltip.hidden=false;
      button.setAttribute('aria-expanded','true');
      section.classList.add('studio-smart-search-help-open');
    }
    function close() {
      cancelPendingClose();
      if (!opened) return;
      opened=false;
      tooltip.hidden=true;
      button.setAttribute('aria-expanded','false');
      section.classList.remove('studio-smart-search-help-open');
    }
    function schedulePointerClose() {
      // The help panel is below the ? button. Allow a brief diagonal move
      // across the visual gap; entering the panel cancels this close.
      cancelPendingClose();
      closeTimer=setTimeout(()=>{
        closeTimer=null;
        if (!holder.contains(document.activeElement)) close();
      },200);
    }
    holder.addEventListener('pointerenter',open);
    holder.addEventListener('pointerleave',schedulePointerClose);
    tooltip.addEventListener('pointerenter',open);
    holder.addEventListener('focusin',open);
    holder.addEventListener('focusout',event=>{if (!holder.contains(event.relatedTarget)) close();});
    button.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();close();button.blur();}});
    document.addEventListener('pointerdown',event=>{if(opened&&!holder.contains(event.target))close();});
    return Object.freeze({open,close,isOpen:()=>opened});
  }
  return Object.freeze({setup,markdown});
})();

document.addEventListener('DOMContentLoaded', () => {
  StudioSmartSearchHelp.setup({
    holder:document.getElementById('studioSmartSearchHelpHolder'),
    button:document.getElementById('studioSmartSearchHelpButton'),
    tooltip:document.getElementById('studioSmartSearchHelpTooltip'),
    section:document.getElementById('searchSection')
  });
});
