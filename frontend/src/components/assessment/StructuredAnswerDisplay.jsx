import {
  isStructuredAnswer,
  parseStructuredAnswer,
  structuredAnswerToPlainText,
} from "../../utils/structuredAnswer";
import LatexPreview from "./LatexPreview";

/** Read-only display of structured maths/science answers on evaluation page. */
const StructuredAnswerDisplay = ({ answer }) => {
  if (!answer) return <span className="text-muted">—</span>;

  if (!isStructuredAnswer(answer)) {
    return <p className="whitespace-pre-wrap text-sm text-foreground">{answer}</p>;
  }

  const data = parseStructuredAnswer(answer);

  return (
    <div className="space-y-4">
      {data.working?.trim() && (
        <div>
          <p className="ds-mono-label mb-1">Working</p>
          <div className="rounded-lg border border-border bg-surface p-3">
            <LatexPreview content={data.working} />
          </div>
        </div>
      )}
      {data.final?.trim() && (
        <div>
          <p className="ds-mono-label mb-1">Final answer</p>
          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3">
            <LatexPreview content={data.final} />
          </div>
        </div>
      )}
      {data.graph?.image && (
        <div>
          <p className="ds-mono-label mb-1">Graph / diagram</p>
          {data.graph.caption && (
            <p className="mb-2 text-xs text-muted">{data.graph.caption}</p>
          )}
          <img
            src={data.graph.image}
            alt="Student graph sketch"
            className="max-w-full rounded-lg border border-border"
          />
        </div>
      )}
      <details className="text-xs text-muted">
        <summary className="cursor-pointer font-mono">Plain text sent to grader</summary>
        <pre className="mt-2 whitespace-pre-wrap rounded bg-surface p-2 font-mono text-[10px]">
          {structuredAnswerToPlainText(answer)}
        </pre>
      </details>
    </div>
  );
};

export default StructuredAnswerDisplay;
