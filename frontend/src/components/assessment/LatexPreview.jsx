import { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

/**
 * Renders mixed text + inline LaTeX ($...$) and display math ($$...$$).
 */
const LatexPreview = ({ content, className = "" }) => {
  const html = useMemo(() => renderMixedLatex(content || ""), [content]);

  if (!content?.trim()) {
    return (
      <p className={`font-mono text-xs italic text-muted ${className}`}>
        Preview appears here as you type…
      </p>
    );
  }

  return (
    <div
      className={`latex-preview min-h-[2.5rem] text-sm leading-relaxed text-foreground ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};

function renderMixedLatex(text) {
  const escapeHtml = (s) =>
    s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

  const renderLatex = (latex, displayMode) => {
    try {
      return katex.renderToString(latex, {
        displayMode,
        throwOnError: false,
        strict: "ignore",
      });
    } catch {
      return `<span class="text-danger">${escapeHtml(latex)}</span>`;
    }
  };

  let out = "";
  let i = 0;
  while (i < text.length) {
    if (text.startsWith("$$", i)) {
      const end = text.indexOf("$$", i + 2);
      if (end !== -1) {
        out += renderLatex(text.slice(i + 2, end), true);
        i = end + 2;
        continue;
      }
    }
    if (text[i] === "$") {
      const end = text.indexOf("$", i + 1);
      if (end !== -1) {
        out += renderLatex(text.slice(i + 1, end), false);
        i = end + 1;
        continue;
      }
    }
    const nextDollar = text.indexOf("$", i);
    const chunkEnd = nextDollar === -1 ? text.length : nextDollar;
    const chunk = text.slice(i, chunkEnd);
    out += escapeHtml(chunk).replace(/\n/g, "<br/>");
    i = chunkEnd;
  }
  return out;
}

export default LatexPreview;
