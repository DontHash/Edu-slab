/**
 * Structured answer format for maths/science assessments.
 * Serialized as JSON string when submitted; flattened to plain text for AI grading.
 */

export const STRUCTURED_ANSWER_VERSION = 1;

export function createEmptyStructuredAnswer() {
  return {
    v: STRUCTURED_ANSWER_VERSION,
    working: "",
    final: "",
    graph: null,
  };
}

export function isStructuredAnswer(value) {
  if (!value || typeof value !== "string") return false;
  const t = value.trim();
  if (!t.startsWith("{")) return false;
  try {
    const data = JSON.parse(t);
    return data?.v === STRUCTURED_ANSWER_VERSION;
  } catch {
    return false;
  }
}

export function parseStructuredAnswer(value) {
  if (!value) return createEmptyStructuredAnswer();
  if (typeof value === "object" && value.v === STRUCTURED_ANSWER_VERSION) {
    return { ...createEmptyStructuredAnswer(), ...value };
  }
  if (typeof value === "string" && isStructuredAnswer(value)) {
    try {
      return { ...createEmptyStructuredAnswer(), ...JSON.parse(value) };
    } catch {
      return createEmptyStructuredAnswer();
    }
  }
  return { ...createEmptyStructuredAnswer(), final: String(value) };
}

export function serializeStructuredAnswer(data) {
  return JSON.stringify({
    v: STRUCTURED_ANSWER_VERSION,
    working: data.working || "",
    final: data.final || "",
    graph: data.graph || null,
  });
}

export function structuredAnswerHasContent(data) {
  const parsed = typeof data === "string" ? parseStructuredAnswer(data) : data;
  return Boolean(
    (parsed.working && parsed.working.trim()) ||
      (parsed.final && parsed.final.trim()) ||
      parsed.graph?.image
  );
}

/** Plain text sent to the grader (LaTeX kept for context). */
export function structuredAnswerToPlainText(value) {
  const data = parseStructuredAnswer(value);
  const parts = [];
  if (data.working?.trim()) {
    parts.push(`WORKING:\n${data.working.trim()}`);
  }
  if (data.final?.trim()) {
    parts.push(`FINAL ANSWER:\n${data.final.trim()}`);
  }
  if (data.graph?.image) {
    parts.push("[Student attached a graph or diagram sketch.]");
    if (data.graph?.caption?.trim()) {
      parts.push(`GRAPH NOTE: ${data.graph.caption.trim()}`);
    }
  }
  return parts.join("\n\n") || (typeof value === "string" ? value : "");
}

export function isStemSubject(subject) {
  const s = (subject || "").toLowerCase();
  return s === "maths" || s === "math" || s === "mathematics" || s === "science";
}
