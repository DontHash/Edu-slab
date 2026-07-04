import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../../components/layout/DashboardLayout";
import StructuredAnswerEditor from "../../components/assessment/StructuredAnswerEditor";
import ragQuestionService from "../../services/ragQuestion.service";
import useAuthStore from "../../store/authStore";
import {
  createEmptyStructuredAnswer,
  isStemSubject,
  serializeStructuredAnswer,
  structuredAnswerHasContent,
} from "../../utils/structuredAnswer";

const TOTAL_QUESTIONS = 10;

const diffBadge = {
  easy: "ds-badge-primary",
  medium: "ds-badge-warn",
  hard: "ds-badge-danger",
};

const RAGAssessmentPage = () => {
  const { user, refreshUser } = useAuthStore();
  const navigate = useNavigate();
  const [step, setStep] = useState("select");
  const [subjects] = useState(["maths", "science", "english"]);
  const [selectedSubject, setSelectedSubject] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [difficulty, setDifficulty] = useState("medium");
  const [progressPercent, setProgressPercent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [curriculumInfo, setCurriculumInfo] = useState(null);
  const [evalEngine, setEvalEngine] = useState(null);
  const grade = user?.current_level || 10;

  useEffect(() => {
    ragQuestionService.getCurriculum(grade).then(setCurriculumInfo).catch(() => {});
    ragQuestionService.getEvaluationStatus().then(setEvalEngine).catch(() => {});
  }, [grade]);

  const resetSession = () => {
    setStep("select");
    setSessionId(null);
    setCurrentQuestion(null);
    setQuestionNumber(1);
    setDifficulty("medium");
    setProgressPercent(0);
    setAnswer("");
    setLastResult(null);
    setError(null);
  };

  const resetAnswerForSubject = (subject) => {
    if (isStemSubject(subject)) {
      setAnswer(serializeStructuredAnswer(createEmptyStructuredAnswer()));
    } else {
      setAnswer("");
    }
  };

  const handleStartAssessment = async () => {
    if (!selectedSubject) {
      setError("Please select a subject");
      return;
    }
    try {
      setStep("loading");
      setLoading(true);
      setError(null);
      const data = await ragQuestionService.startAdaptiveSession(selectedSubject, grade);
      setSessionId(data.session_id);
      setCurrentQuestion(data.question);
      setQuestionNumber(data.question_number);
      setDifficulty(data.difficulty);
      setProgressPercent(data.progress_percent);
      resetAnswerForSubject(selectedSubject);
      setLastResult(null);
      setStep("question");
    } catch (err) {
      setError("Failed to start: " + (err.response?.data?.detail || err.message));
      setStep("select");
    } finally {
      setLoading(false);
    }
  };

  const handleFinishAndEvaluate = async (sid) => {
    try {
      setLoading(true);
      const result = await ragQuestionService.finishAdaptiveSession(sid);
      try { await refreshUser(); } catch (_) {}
      navigate(`/assessment-evaluation/${result.assessment_id}`);
    } catch (err) {
      setError("Failed to generate report: " + (err.response?.data?.detail || err.message));
      setStep("completed");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    const hasContent = isStemSubject(selectedSubject)
      ? structuredAnswerHasContent(answer)
      : Boolean(answer?.trim());

    if (!hasContent) {
      setError(
        isStemSubject(selectedSubject)
          ? "Add a final answer, working steps, or a graph before continuing."
          : "Please enter your answer before continuing."
      );
      return;
    }
    if (!sessionId || !currentQuestion) return;
    try {
      setLoading(true);
      setError(null);
      const payload = isStemSubject(selectedSubject) ? answer : answer.trim();
      const data = await ragQuestionService.submitAdaptiveAnswer(
        sessionId, currentQuestion.id, payload
      );
      setLastResult(data.last_result);
      setProgressPercent(data.progress_percent);
      if (data.completed) {
        setStep("finishing");
        await handleFinishAndEvaluate(sessionId);
        return;
      }
      setCurrentQuestion(data.question);
      setQuestionNumber(data.question_number);
      setDifficulty(data.difficulty);
      resetAnswerForSubject(selectedSubject);
    } catch (err) {
      setError("Failed to submit: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const renderSelect = () => (
    <div className="mx-auto max-w-2xl ds-panel-raised p-8 animate-slide-up">
      <p className="ds-mono-label mb-2 text-primary">Adaptive · 10 questions</p>
      <h2 className="text-2xl font-bold text-foreground">Start diagnostic</h2>
      <p className="mt-2 text-sm text-muted">
        Grade {grade} content — difficulty starts at your level and adjusts with each answer.
      </p>
      {evalEngine && !evalEngine.ollama?.model_ready && (
        <div className="mt-4 rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
          AI grader offline — answers will need re-evaluation for full scoring.
        </div>
      )}
      {curriculumInfo && (
        <p className="mt-1 font-mono text-[10px] uppercase tracking-wider text-muted">
          {curriculumInfo.framework}
        </p>
      )}
      {curriculumInfo?.subjects && (
        <p className="mt-2 text-xs text-muted">
          Full blueprint diagnostics:{" "}
          {Object.entries(curriculumInfo.subjects)
            .filter(([, v]) => v.blueprint_ready)
            .map(([k]) => k.charAt(0).toUpperCase() + k.slice(1))
            .join(", ") || "legacy mode for this grade"}
        </p>
      )}
      {error && (
        <div className="mt-4 rounded-lg border border-danger/30 bg-danger/10 p-4 text-sm text-danger">
          {error}
        </div>
      )}
      <div className="mt-6">
        <label className="ds-mono-label mb-2 block">Subject</label>
        <select
          value={selectedSubject}
          onChange={(e) => {
            setSelectedSubject(e.target.value);
            resetAnswerForSubject(e.target.value);
          }}
          className="ds-input"
        >
          <option value="">Select subject…</option>
          {subjects.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>
      <button
        onClick={handleStartAssessment}
        disabled={!selectedSubject || loading}
        className="ds-btn-primary mt-6 w-full disabled:opacity-40"
      >
        {loading ? "Starting…" : "Begin assessment"}
      </button>
    </div>
  );

  const renderQuestion = () => (
    <div className="mx-auto max-w-3xl ds-panel-raised p-8 animate-slide-up">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <p className="ds-mono-label text-primary capitalize">{selectedSubject}</p>
          <h2 className="text-xl font-bold text-foreground">
            Question {questionNumber}
            <span className="font-mono text-muted"> / {TOTAL_QUESTIONS}</span>
          </h2>
        </div>
        <button onClick={resetSession} className="ds-btn-ghost text-sm">Exit</button>
      </div>

      <div className="mb-6">
        <div className="mb-2 flex justify-between font-mono text-[10px] uppercase tracking-widest text-muted">
          <span>Progress</span>
          <span>{progressPercent}%</span>
        </div>
        <div className="ds-progress-track">
          <div className="ds-progress-fill" style={{ width: `${progressPercent}%` }} />
        </div>
      </div>

      {lastResult && (
        <div className={`mb-4 rounded-lg border p-3 text-sm ${
          lastResult.correct
            ? "border-primary/30 bg-primary/10 text-primary"
            : lastResult.partial
            ? "border-warning/30 bg-warning/10 text-warning"
            : "border-danger/30 bg-danger/10 text-danger"
        }`}>
          {lastResult.method === "unresolved"
            ? "Answer recorded — full grading after completion."
            : lastResult.correct
            ? "Correct — level up."
            : lastResult.partial
            ? "Partial — holding level."
            : "Incorrect — easing difficulty."}
          {lastResult.next_difficulty && (
            <span className="ml-2 font-mono text-xs opacity-80">→ {lastResult.next_difficulty}</span>
          )}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg border border-danger/30 bg-danger/10 p-4 text-sm text-danger">{error}</div>
      )}

      {currentQuestion && (
        <div className="mb-6 rounded-xl border border-border bg-surface p-5">
          <div className="mb-4 flex flex-wrap gap-2">
            <span className="ds-badge-muted">{currentQuestion.chapter}</span>
            {currentQuestion.domain && (
              <span className="rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-primary">
                {currentQuestion.domain.replace(/_/g, " ")}
              </span>
            )}
            {currentQuestion.section && (
              <span className="rounded-full border border-border bg-surface-raised px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted">
                {currentQuestion.section.replace(/_/g, " ")}
              </span>
            )}
            {currentQuestion.generative && (
              <span className="rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-primary">
                generated
              </span>
            )}
            <span className={diffBadge[difficulty] || diffBadge.medium}>{difficulty}</span>
          </div>
          {currentQuestion.context_text && (
            <div className="mb-5 rounded-lg border border-border/80 bg-surface-raised p-4">
              <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted">Reading passage</p>
              <div
                className="prose-sm whitespace-pre-wrap leading-relaxed text-foreground [&_strong]:text-primary"
                dangerouslySetInnerHTML={{
                  __html: currentQuestion.context_text
                    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                    .replace(/\n/g, "<br/>"),
                }}
              />
            </div>
          )}
          <div
            className="prose-sm whitespace-pre-wrap leading-relaxed text-foreground [&_strong]:text-primary"
            dangerouslySetInnerHTML={{
              __html: currentQuestion.question
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                .replace(/\n/g, "<br/>"),
            }}
          />
        </div>
      )}

      {isStemSubject(selectedSubject) ? (
        <StructuredAnswerEditor
          subject={selectedSubject}
          value={answer}
          onChange={setAnswer}
          disabled={loading}
        />
      ) : (
        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Write your answer…"
          rows={5}
          disabled={loading}
          className="ds-input resize-none disabled:opacity-50"
        />
      )}

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleSubmitAnswer}
          disabled={
            loading ||
            !(isStemSubject(selectedSubject)
              ? structuredAnswerHasContent(answer)
              : answer?.trim())
          }
          className="ds-btn-primary px-8 disabled:opacity-40"
        >
          {loading ? "Checking…" : questionNumber >= TOTAL_QUESTIONS ? "Submit final answer" : "Submit & continue"}
        </button>
      </div>
    </div>
  );

  const renderLoading = () => (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4">
      <div className="h-12 w-12 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      <p className="font-mono text-xs uppercase tracking-widest text-muted">
        {step === "finishing" ? "Building your report…" : "Loading question…"}
      </p>
    </div>
  );

  return (
    <DashboardLayout>
      <div className="animate-fade-in">
        <header className="ds-page-header mb-8">
          <p className="ds-mono-label mb-2 text-primary">Live diagnostic</p>
          <h1 className="ds-page-title">Adaptive assessment</h1>
          <p className="ds-page-subtitle">
            Contextual questions that respond to how you perform.
          </p>
        </header>
        {step === "loading" || step === "finishing" ? renderLoading() : step === "question" ? renderQuestion() : renderSelect()}
      </div>
    </DashboardLayout>
  );
};

export default RAGAssessmentPage;
