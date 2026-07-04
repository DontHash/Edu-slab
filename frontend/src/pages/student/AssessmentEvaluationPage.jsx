import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import StructuredAnswerDisplay from "../../components/assessment/StructuredAnswerDisplay";
import api from "../../services/api";
import ragQuestionService from "../../services/ragQuestion.service";

const scoreColor = (pct) => {
  if (pct >= 85) return "text-primary";
  if (pct >= 70) return "text-warning";
  if (pct >= 50) return "text-orange-400";
  return "text-danger";
};

const weaknessClass = (level) => {
  if (level === "none") return "ds-badge-primary";
  if (level === "severe") return "ds-badge-danger";
  if (level === "moderate") return "ds-badge-warn";
  return "ds-badge-muted";
};

const ResourceCard = ({ resource }) => (
  <a href={resource.url} target="_blank" rel="noopener noreferrer" className="ds-resource-link">
    <div className="flex flex-wrap items-center gap-2">
      <span className="ds-badge-primary">{resource.provider_label || resource.provider}</span>
      {resource.url_verified && (
        <span className="font-mono text-[10px] text-primary">verified link</span>
      )}
    </div>
    <p className="mt-2 text-sm font-semibold text-foreground">{resource.title}</p>
    {resource.description && <p className="mt-1 text-xs text-muted">{resource.description}</p>}
    {resource.topic_match && (
      <p className="mt-1 font-mono text-[10px] text-muted">Matched: {resource.topic_match}</p>
    )}
    {resource.chapter && <p className="mt-1 font-mono text-[10px] text-muted">{resource.chapter}</p>}
    <p className="mt-2 text-xs font-semibold text-primary">Open tutorial →</p>
  </a>
);

const AssessmentEvaluationPage = () => {
  const { assessmentId } = useParams();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [evalEngine, setEvalEngine] = useState(null);

  useEffect(() => {
    loadEvaluation();
    ragQuestionService.getEvaluationStatus().then(setEvalEngine).catch(() => {});
  }, [assessmentId]);

  const loadEvaluation = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/rag/evaluate-assessment/${assessmentId}`);
      setEvaluation(response.data);
    } catch (err) {
      if (err.response?.status === 404) handleEvaluate();
      else setError("Failed to load evaluation");
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async () => {
    try {
      setEvaluating(true);
      setError(null);
      const response = await api.post(`/rag/evaluate-assessment/${assessmentId}`);
      setEvaluation(response.data);
    } catch (err) {
      setError("Failed to evaluate: " + (err.response?.data?.detail || err.message));
    } finally {
      setEvaluating(false);
    }
  };

  const shell = (children) => (
    <div className="ds-ambient min-h-screen">
      <div className="pointer-events-none fixed inset-x-0 top-0 h-64 ds-gradient-scrim" />
      <div className="relative mx-auto max-w-6xl px-4 py-8 sm:px-6">{children}</div>
    </div>
  );

  if (loading) {
    return shell(
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <p className="font-mono text-xs uppercase tracking-widest text-muted">Loading report…</p>
      </div>
    );
  }

  if (!evaluation) {
    return shell(
      <div className="mx-auto max-w-lg ds-panel-raised p-8 text-center animate-slide-up">
        <h2 className="text-2xl font-bold text-foreground">Report pending</h2>
        <p className="mt-2 text-sm text-muted">Run AI evaluation to generate your diagnostic report.</p>
        <button onClick={handleEvaluate} disabled={evaluating} className="ds-btn-primary mt-6 disabled:opacity-40">
          {evaluating ? "Evaluating…" : "Evaluate now"}
        </button>
        {error && <p className="mt-4 text-sm text-danger">{error}</p>}
      </div>
    );
  }

  const { chapter_analysis, domain_analysis, overall_analysis, learning_outcome_analysis, recommended_resources, question_analysis, answers } = evaluation;
  const loAnalysis = learning_outcome_analysis || overall_analysis?.learning_outcome_analysis || {};
  const studyPlan = overall_analysis?.study_plan;
  const weakTopics = studyPlan?.weak_topics || [];
  const unresolved = overall_analysis?.unresolved_questions || 0;
  const answerById = Object.fromEntries((answers || []).map((a) => [a.question_id, a]));

  return shell(
    <div className="animate-fade-in space-y-8">
      <header className="ds-page-header">
        <button onClick={() => navigate("/dashboard")} className="ds-btn-ghost mb-4 -ml-2 text-sm">
          ← Dashboard
        </button>
        <p className="ds-mono-label mb-2 text-primary">Diagnostic report</p>
        <h1 className="ds-page-title">Topic assessment</h1>
        {overall_analysis?.evaluation_method && (
          <p className="mt-2 font-mono text-[10px] uppercase tracking-widest text-muted">
            {overall_analysis.evaluation_method.replace(/_/g, " ")}
          </p>
        )}
        {evalEngine && !evalEngine.ollama?.model_ready && (
          <p className="mt-2 text-sm text-warning">
            AI grader offline — {evalEngine.message}
          </p>
        )}
      </header>

      {unresolved > 0 && (
        <div className="rounded-lg border border-warning/40 bg-warning/10 p-4 text-sm text-warning">
          {unresolved} answer(s) could not be fully verified. Scores may be conservative.
          Re-run evaluation when Ollama is online for a complete report.
        </div>
      )}

      {/* Score hero */}
      <div className="relative overflow-hidden rounded-2xl border border-border bg-surface-raised p-8 shadow-glow">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent" />
        <div className="relative grid gap-6 md:grid-cols-3">
          <div>
            <p className="ds-stat-label">Final score</p>
            <p className="mt-1 font-mono text-5xl font-medium text-primary">
              {overall_analysis?.final_score_out_of_100 || 0}
            </p>
            <p className="text-xs text-muted">out of 100</p>
          </div>
          <div>
            <p className="ds-stat-label">Estimated grade</p>
            <p className="mt-1 font-mono text-5xl font-medium text-foreground">
              {overall_analysis?.estimated_student_grade_level || "—"}
            </p>
            {overall_analysis?.proficiency_label && (
              <p className="mt-1 text-xs text-muted">{overall_analysis.proficiency_label}</p>
            )}
          </div>
          <div>
            <p className="ds-stat-label mb-2">Strongest</p>
            {(overall_analysis?.strongest_chapters || []).map((ch, i) => (
              <p key={i} className="text-sm text-primary">✓ {ch}</p>
            ))}
          </div>
        </div>
      </div>

      {(domain_analysis && Object.keys(domain_analysis).length > 0) ||
      (overall_analysis?.domain_analysis && Object.keys(overall_analysis.domain_analysis).length > 0) ? (
        <div className="ds-panel p-6">
          <p className="ds-mono-label mb-4 text-primary">Domain breakdown</p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(domain_analysis || overall_analysis.domain_analysis).map(([domain, data]) => (
              <div key={domain} className="rounded-lg border border-border bg-surface-raised p-4">
                <p className="font-medium capitalize text-foreground">{domain.replace(/_/g, " ")}</p>
                <p className="mt-1 font-mono text-2xl text-primary">{data.accuracy_percentage}%</p>
                <p className="text-xs text-muted">
                  {data.correct} correct · {data.partial} partial · {data.incorrect} incorrect
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {Object.keys(loAnalysis).length > 0 && (
        <div className="ds-panel p-6">
          <p className="ds-mono-label mb-4 text-primary">Learning outcomes</p>
          <div className="space-y-2">
            {Object.entries(loAnalysis)
              .sort((a, b) => a[1].accuracy_percentage - b[1].accuracy_percentage)
              .map(([loId, data]) => (
                <div
                  key={loId}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border bg-surface-raised px-4 py-3"
                >
                  <span className="font-mono text-xs text-muted">{loId}</span>
                  <div className="flex items-center gap-3">
                    <span className={weaknessClass(data.weakness_level)}>{data.weakness_level}</span>
                    <span className="font-mono text-sm text-primary">{data.accuracy_percentage}%</span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {overall_analysis?.learning_gap_summary?.length > 0 && (
        <div className="ds-panel p-6">
          <p className="ds-mono-label mb-3 text-warning">Learning gaps</p>
          <ul className="space-y-2 text-sm text-muted">
            {overall_analysis.learning_gap_summary.map((gap, i) => (
              <li key={i} className="flex gap-2"><span className="text-warning">→</span>{gap}</li>
            ))}
          </ul>
        </div>
      )}

      {weakTopics.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-foreground">Your study plan</h2>
          {weakTopics.map((topic, idx) => (
            <div key={idx} className="ds-panel-raised p-6 animate-slide-up">
              <div className="mb-4 flex flex-wrap items-center gap-2">
                <h3 className="font-semibold text-foreground">{topic.chapter}</h3>
                <span className={weaknessClass(topic.weakness_level)}>{topic.weakness_level}</span>
                <span className="font-mono text-xs text-muted">{topic.accuracy_percentage}%</span>
              </div>
              {topic.study_steps?.length > 0 && (
                <ol className="mb-4 list-decimal space-y-1 pl-5 text-sm text-muted">
                  {topic.study_steps.map((s, i) => <li key={i}>{s}</li>)}
                </ol>
              )}
              {topic.recommended_resources?.length > 0 && (
                <div className="grid gap-3 md:grid-cols-2">
                  {topic.recommended_resources.map((r, i) => (
                    <ResourceCard key={i} resource={r} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {(recommended_resources?.length > 0 || studyPlan?.all_resources?.length > 0) && (
        <div className="ds-panel p-6">
          <h2 className="mb-4 text-xl font-bold text-foreground">Free learning resources</h2>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {(recommended_resources || studyPlan?.all_resources || []).map((r, i) => (
              <ResourceCard key={i} resource={r} />
            ))}
          </div>
        </div>
      )}

      <div className="ds-panel p-6">
        <h2 className="mb-6 text-xl font-bold text-foreground">Question-by-question</h2>
        <div className="space-y-4">
          {Object.entries(question_analysis || {}).map(([qid, data]) => {
            const ans = answerById[qid];
            const verdictClass =
              data.correctness === "correct"
                ? "border-primary/30"
                : data.correctness === "partial"
                ? "border-warning/30"
                : "border-danger/30";
            return (
              <div key={qid} className={`rounded-xl border bg-surface p-4 ${verdictClass}`}>
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="ds-badge-muted">{ans?.chapter || "Topic"}</span>
                  <span className={weaknessClass(data.correctness === "correct" ? "none" : "moderate")}>
                    {data.correctness}
                  </span>
                  <span className="font-mono text-xs text-muted">score {data.score}</span>
                  {data.grading_method && (
                    <span className="font-mono text-[10px] text-muted">{data.grading_method}</span>
                  )}
                </div>
                <p className="text-sm text-foreground">{ans?.question_raw || ans?.question || "Question"}</p>
                <div className="mt-2">
                  <StructuredAnswerDisplay answer={ans?.answer} />
                </div>
                {data.medium_reason && (
                  <p className="mt-2 text-xs text-warning">{data.medium_reason}</p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="ds-panel p-6">
        <h2 className="mb-6 text-xl font-bold text-foreground">Chapter breakdown</h2>
        <div className="grid max-h-[36rem] grid-cols-1 gap-4 overflow-y-auto pr-1 md:grid-cols-2 lg:grid-cols-3">
          {Object.entries(chapter_analysis || {}).map(([chapter, data]) => (
            <div key={chapter} className="rounded-xl border border-border bg-surface p-4 transition-all hover:border-primary/25">
              <h3 className="font-semibold text-foreground">{chapter}</h3>
              <div className="ds-progress-track my-3">
                <div className="ds-progress-fill" style={{ width: `${data.accuracy_percentage}%` }} />
              </div>
              <div className="flex items-center justify-between">
                <span className={`font-mono text-2xl ${scoreColor(data.accuracy_percentage)}`}>
                  {data.accuracy_percentage}%
                </span>
                <span className={weaknessClass(data.weakness_level)}>{data.weakness_level}</span>
              </div>
              <div className="mt-3 space-y-1 font-mono text-[10px] text-muted">
                <div className="flex justify-between"><span>Correct</span><span className="text-primary">{data.correct}/{data.total_questions}</span></div>
                <div className="flex justify-between"><span>Score</span><span>{data.chapter_score_out_of_10}/10</span></div>
              </div>
              {data.recommended_resources?.slice(0, 1).map((r, i) => (
                <a key={i} href={r.url} target="_blank" rel="noopener noreferrer" className="mt-3 block text-xs font-semibold text-primary hover:underline">
                  {r.title} →
                </a>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link to="/assessment" className="ds-btn-primary">New assessment</Link>
        <Link to="/resources" className="ds-btn-outline">Learning roadmap</Link>
        <button onClick={() => window.print()} className="ds-btn-ghost">Print</button>
      </div>
    </div>
  );
};

export default AssessmentEvaluationPage;
