import { useRef, useState } from "react";
import {
  createEmptyStructuredAnswer,
  parseStructuredAnswer,
  serializeStructuredAnswer,
} from "../../utils/structuredAnswer";
import GraphSketchPad from "./GraphSketchPad";
import LatexPreview from "./LatexPreview";
import MathSymbolPalette from "./MathSymbolPalette";

const TABS = [
  { id: "working", label: "Working", hint: "Steps, formulas, reasoning" },
  { id: "final", label: "Final answer", hint: "Required result" },
  { id: "graph", label: "Graph / diagram", hint: "Plots, geometry, circuits" },
];

const StructuredAnswerEditor = ({ subject, value, onChange, disabled }) => {
  const parsed = parseStructuredAnswer(value);
  const [tab, setTab] = useState("working");
  const workingRef = useRef(null);
  const finalRef = useRef(null);

  const update = (patch) => {
    const next = { ...createEmptyStructuredAnswer(), ...parsed, ...patch };
    if (next.graph && !next.graph.image) next.graph = null;
    onChange(serializeStructuredAnswer(next));
  };

  const setField = (field, text) => update({ [field]: text });

  const activeRef = tab === "final" ? finalRef : workingRef;

  const handleSymbolInsert = (text) => {
    if (tab === "graph" || typeof text !== "string") return;
    const field = tab === "final" ? "final" : "working";
    setField(field, text);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-1 rounded-lg border border-border bg-surface p-1">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            disabled={disabled}
            onClick={() => setTab(t.id)}
            className={`min-w-[7rem] flex-1 rounded-md px-3 py-2 text-left transition-colors ${
              tab === t.id
                ? "bg-primary/15 text-primary"
                : "text-muted hover:bg-surface-raised hover:text-foreground"
            }`}
          >
            <span className="block text-sm font-semibold">{t.label}</span>
            <span className="font-mono text-[10px] opacity-70">{t.hint}</span>
          </button>
        ))}
      </div>

      {tab !== "graph" && (
        <MathSymbolPalette
          subject={subject}
          targetRef={activeRef}
          onInsert={handleSymbolInsert}
        />
      )}

      {tab === "working" && (
        <div className="space-y-2">
          <label className="ds-mono-label">Working / steps</label>
          <textarea
            ref={workingRef}
            value={parsed.working || ""}
            onChange={(e) => setField("working", e.target.value)}
            disabled={disabled}
            rows={6}
            placeholder={"e.g.\nn(A) = 5, n(B) = 3\nn(A × B) = 5 × 3 = 15"}
            className="ds-input resize-y font-mono text-sm leading-relaxed"
          />
          <div className="rounded-lg border border-border bg-surface-raised p-3">
            <p className="ds-mono-label mb-2">Live preview</p>
            <LatexPreview content={parsed.working} />
          </div>
        </div>
      )}

      {tab === "final" && (
        <div className="space-y-2">
          <label className="ds-mono-label">Final answer *</label>
          <textarea
            ref={finalRef}
            value={parsed.final || ""}
            onChange={(e) => setField("final", e.target.value)}
            disabled={disabled}
            rows={3}
            placeholder="e.g. n(A × B) = 15  or  Rs. 12,500"
            className="ds-input resize-y font-mono text-sm"
          />
          <div className="rounded-lg border border-border bg-surface-raised p-3">
            <p className="ds-mono-label mb-2">Live preview</p>
            <LatexPreview content={parsed.final} />
          </div>
        </div>
      )}

      {tab === "graph" && (
        <GraphSketchPad
          value={parsed.graph}
          caption={parsed.graph?.caption || ""}
          onCaptionChange={(caption) =>
            update({
              graph: parsed.graph
                ? { ...parsed.graph, caption }
                : { caption, elements: [] },
            })
          }
          onChange={(graph) =>
            update({
              graph: graph
                ? { ...graph, caption: graph.caption ?? parsed.graph?.caption ?? "" }
                : null,
            })
          }
        />
      )}
    </div>
  );
};

export default StructuredAnswerEditor;
