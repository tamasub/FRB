// studio_work_0268: Small, non-editing hover/focus help for the Smart Search grammar.
// Keep the help as Markdown; use the existing Studio Markdown renderer.
var StudioSmartSearchHelp = (function () {
  'use strict';

  const markdown = [
    '### Smart Search の書き方',
    '',
    '- `単語A 単語B` — **空白区切りはAND**（両方に一致）',
    '- `単語A or 単語B` — **OR**（どちらかに一致。`OR` も可）',
    '- `(単語A or 単語B) 単語C` — **括弧**で条件をまとめる',
    '- `種別=feature` — **項目指定**（文字列は部分一致、数値・選択肢等は一致）',
    '- `種別==feature` — **完全一致**',
    '- `種別!=bug` / `種別=!bug` — **不一致**',
    '- `t>1` / `t>=1` / `t<2` / `t<=2` — **大小比較**（数値・日付系のみ）',
    '- `t=>1` / `t=<2` — `>=` / `<=` と同じ意味',
    '- `t=1.1..1.8` — **範囲指定**（両端を含む。数値・日付系）',
    '- `t=1..` / `t=..5` — **片側を省略した範囲**',
    '- `"Flux A">=0.1` — **空白を含む項目名**は引用符で囲む',
    '- `"重要 案件"` — **空白を含む検索語**も引用符で囲む',
    '',
    '### 入力補完',
    '',
    '- `/` または検索欄の **右クリック** — 項目候補を表示（`/` は検索式に入らない）',
    '- `↑` / `↓` — 候補移動、`Tab` / `Enter` / `→` — 候補確定、`Esc` — 閉じる',
    '- 候補一覧内の検索欄で項目・選択値を絞り込み可能',
    '',
    '> 項目名は表示名でも項目IDでも指定できます。',
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
