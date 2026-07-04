import { useState } from "react";
import { getSymbolGroups } from "./mathSymbols";

/**
 * University-style symbol toolbar — inserts LaTeX at cursor in target textarea.
 */
const MathSymbolPalette = ({ subject, targetRef, onInsert }) => {
  const [openGroup, setOpenGroup] = useState("Basic");
  const groups = getSymbolGroups(subject);

  const insertAtCursor = (symbol) => {
    const el = targetRef?.current;
    if (!el) {
      onInsert?.(symbol.insert);
      return;
    }

    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? start;
    const before = el.value.slice(0, start);
    const after = el.value.slice(end);
    const next = before + symbol.insert + after;
    onInsert?.(next);

    requestAnimationFrame(() => {
      el.focus();
      const offset = symbol.cursorOffset ?? 0;
      const pos = start + symbol.insert.length + offset;
      el.setSelectionRange(pos, pos);
    });
  };

  return (
    <div className="rounded-lg border border-border bg-surface">
      <div className="flex flex-wrap gap-1 border-b border-border p-2">
        {groups.map((g) => (
          <button
            key={g.label}
            type="button"
            onClick={() => setOpenGroup(g.label)}
            className={`rounded px-2 py-1 font-mono text-[10px] uppercase tracking-wide transition-colors ${
              openGroup === g.label
                ? "bg-primary/20 text-primary"
                : "text-muted hover:bg-surface-raised hover:text-foreground"
            }`}
          >
            {g.label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-1.5 p-2">
        {(groups.find((g) => g.label === openGroup) || groups[0]).symbols.map((sym) => (
          <button
            key={`${openGroup}-${sym.label}`}
            type="button"
            title={sym.title}
            onClick={() => insertAtCursor(sym)}
            className="min-w-[2.25rem] rounded border border-border bg-surface-raised px-2 py-1.5 font-mono text-sm text-foreground transition-colors hover:border-primary/40 hover:bg-primary/10"
          >
            {sym.label}
          </button>
        ))}
      </div>
      <p className="border-t border-border px-2 py-1.5 font-mono text-[10px] text-muted">
        Tip: use ^ for powers, _ for subscripts, \\frac{"{a}{b}"} for fractions
      </p>
    </div>
  );
};

export default MathSymbolPalette;
