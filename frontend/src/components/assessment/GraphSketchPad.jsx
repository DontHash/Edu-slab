import { useCallback, useEffect, useRef, useState } from "react";

const W = 480;
const H = 360;
const X_MIN = -10;
const X_MAX = 10;
const Y_MIN = -8;
const Y_MAX = 8;

const TOOLS = [
  { id: "point", label: "Point" },
  { id: "line", label: "Line" },
  { id: "arrow", label: "Arrow" },
  { id: "label", label: "Label" },
];

function toCanvas(x, y) {
  const px = ((x - X_MIN) / (X_MAX - X_MIN)) * W;
  const py = H - ((y - Y_MIN) / (Y_MAX - Y_MIN)) * H;
  return { px, py };
}

function fromCanvas(px, py) {
  const x = X_MIN + (px / W) * (X_MAX - X_MIN);
  const y = Y_MAX - (py / H) * (Y_MAX - Y_MIN);
  return { x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10 };
}

function drawGrid(ctx) {
  ctx.fillStyle = "#1a1d26";
  ctx.fillRect(0, 0, W, H);

  ctx.strokeStyle = "#2a3040";
  ctx.lineWidth = 1;
  for (let x = X_MIN; x <= X_MAX; x++) {
    const { px } = toCanvas(x, 0);
    ctx.beginPath();
    ctx.moveTo(px, 0);
    ctx.lineTo(px, H);
    ctx.stroke();
  }
  for (let y = Y_MIN; y <= Y_MAX; y++) {
    const { py } = toCanvas(0, y);
    ctx.beginPath();
    ctx.moveTo(0, py);
    ctx.lineTo(W, py);
    ctx.stroke();
  }

  ctx.strokeStyle = "#4a5568";
  ctx.lineWidth = 2;
  const ox = toCanvas(0, 0).px;
  const oy = toCanvas(0, 0).py;
  ctx.beginPath();
  ctx.moveTo(0, oy);
  ctx.lineTo(W, oy);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(ox, 0);
  ctx.lineTo(ox, H);
  ctx.stroke();

  ctx.fillStyle = "#6b7280";
  ctx.font = "10px JetBrains Mono, monospace";
  ctx.fillText("x", W - 14, oy - 6);
  ctx.fillText("y", ox + 6, 12);
}

function drawElements(ctx, elements) {
  elements.forEach((el) => {
    ctx.strokeStyle = "#4ade80";
    ctx.fillStyle = "#4ade80";
    ctx.lineWidth = 2;
    ctx.font = "12px JetBrains Mono, monospace";

    if (el.type === "point") {
      const { px, py } = toCanvas(el.x, el.y);
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fill();
      if (el.label) ctx.fillText(el.label, px + 6, py - 6);
    }

    if (el.type === "line" || el.type === "arrow") {
      const a = toCanvas(el.x1, el.y1);
      const b = toCanvas(el.x2, el.y2);
      ctx.beginPath();
      ctx.moveTo(a.px, a.py);
      ctx.lineTo(b.px, b.py);
      ctx.stroke();
      if (el.type === "arrow") {
        const angle = Math.atan2(b.py - a.py, b.px - a.px);
        const len = 10;
        ctx.beginPath();
        ctx.moveTo(b.px, b.py);
        ctx.lineTo(b.px - len * Math.cos(angle - 0.4), b.py - len * Math.sin(angle - 0.4));
        ctx.moveTo(b.px, b.py);
        ctx.lineTo(b.px - len * Math.cos(angle + 0.4), b.py - len * Math.sin(angle + 0.4));
        ctx.stroke();
      }
    }

    if (el.type === "label") {
      const { px, py } = toCanvas(el.x, el.y);
      ctx.fillText(el.text || "", px, py);
    }
  });
}

/**
 * Coordinate graph / diagram sketch pad (assignment-style).
 */
const GraphSketchPad = ({ value, onChange, caption, onCaptionChange }) => {
  const canvasRef = useRef(null);
  const [tool, setTool] = useState("point");
  const [elements, setElements] = useState(value?.elements || []);
  const [pending, setPending] = useState(null);

  const redraw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    drawGrid(ctx);
    drawElements(ctx, elements);
    if (pending) {
      ctx.strokeStyle = "#fbbf24";
      ctx.setLineDash([4, 4]);
      if (pending.type === "line" || pending.type === "arrow") {
        const a = toCanvas(pending.x1, pending.y1);
        const b = toCanvas(pending.x2, pending.y2);
        ctx.beginPath();
        ctx.moveTo(a.px, a.py);
        ctx.lineTo(b.px, b.py);
        ctx.stroke();
      }
      ctx.setLineDash([]);
    }
  }, [elements, pending]);

  useEffect(() => {
    redraw();
  }, [redraw]);

  useEffect(() => {
    if (value?.elements) setElements(value.elements);
  }, [value?.elements]);

  const exportGraph = useCallback(
    (els) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      drawGrid(ctx);
      drawElements(ctx, els);
      const image = canvas.toDataURL("image/png");
      onChange?.({
        image,
        elements: els,
        width: W,
        height: H,
        axes: { x: [X_MIN, X_MAX], y: [Y_MIN, Y_MAX] },
      });
    },
    [onChange]
  );

  const handleCanvasClick = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = W / rect.width;
    const scaleY = H / rect.height;
    const px = (e.clientX - rect.left) * scaleX;
    const py = (e.clientY - rect.top) * scaleY;
    const { x, y } = fromCanvas(px, py);

    if (tool === "point") {
      const label = window.prompt("Point label (optional):", "") || "";
      const next = [...elements, { type: "point", x, y, label: label.trim() }];
      setElements(next);
      exportGraph(next);
      return;
    }

    if (tool === "label") {
      const text = window.prompt("Label text:", "");
      if (!text) return;
      const next = [...elements, { type: "label", x, y, text }];
      setElements(next);
      exportGraph(next);
      return;
    }

    if (tool === "line" || tool === "arrow") {
      if (!pending) {
        setPending({ type: tool, x1: x, y1: y, x2: x, y2: y });
      } else {
        const next = [
          ...elements,
          { type: tool, x1: pending.x1, y1: pending.y1, x2: x, y2: y },
        ];
        setElements(next);
        setPending(null);
        exportGraph(next);
      }
    }
  };

  const handleMouseMove = (e) => {
    if (!pending) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = W / rect.width;
    const scaleY = H / rect.height;
    const px = (e.clientX - rect.left) * scaleX;
    const py = (e.clientY - rect.top) * scaleY;
    const { x, y } = fromCanvas(px, py);
    setPending((p) => (p ? { ...p, x2: x, y2: y } : null));
  };

  const clearGraph = () => {
    setElements([]);
    setPending(null);
    onChange?.(null);
  };

  const undo = () => {
    const next = elements.slice(0, -1);
    setElements(next);
    exportGraph(next);
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {TOOLS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => {
              setTool(t.id);
              setPending(null);
            }}
            className={`rounded border px-3 py-1 font-mono text-xs transition-colors ${
              tool === t.id
                ? "border-primary bg-primary/15 text-primary"
                : "border-border text-muted hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
        <button type="button" onClick={undo} className="ds-btn-ghost text-xs" disabled={!elements.length}>
          Undo
        </button>
        <button type="button" onClick={clearGraph} className="ds-btn-ghost text-xs text-danger">
          Clear
        </button>
      </div>

      <div className="overflow-hidden rounded-lg border border-border">
        <canvas
          ref={canvasRef}
          width={W}
          height={H}
          className="w-full cursor-crosshair bg-surface"
          onClick={handleCanvasClick}
          onMouseMove={handleMouseMove}
        />
      </div>

      <p className="font-mono text-[10px] text-muted">
        {tool === "line" || tool === "arrow"
          ? "Click start point, then end point. Grid: x ∈ [−10, 10], y ∈ [−8, 8]."
          : tool === "point"
          ? "Click to plot a point on the graph."
          : "Click to place a text label."}
      </p>

      <input
        type="text"
        value={caption || ""}
        onChange={(e) => onCaptionChange?.(e.target.value)}
        placeholder="Graph caption (e.g. height vs distance, V–I curve)…"
        className="ds-input text-sm"
      />

      {value?.image && (
        <p className="font-mono text-[10px] text-primary">✓ Graph saved with your answer</p>
      )}
    </div>
  );
};

export default GraphSketchPad;
