import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../../components/layout/DashboardLayout";
import ragQuestionService from "../../services/ragQuestion.service";
import useAuthStore from "../../store/authStore";

const RAGAssessmentPage = () => {
  const { user, refreshUser } = useAuthStore();
  const navigate = useNavigate();
  const [step, setStep] = useState("select"); // 'select', 'loading', 'questions', 'submitted'

  // Chapter selection state
  const [subjects, setSubjects] = useState([]);
  const [chaptersBySubject, setChaptersBySubject] = useState({});
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedChapter, setSelectedChapter] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);

  // Questions state
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Submission state
  const [submittedAssessment, setSubmittedAssessment] = useState(null);

  useEffect(() => {
    // Set subjects directly - no need to fetch from API
    setSubjects(["maths", "science", "english"]);
  }, []);

  const handleGenerateQuestions = async () => {
    if (!selectedSubject) {
      setError("Please select a subject");
      return;
    }

    try {
      setStep("loading");
      setLoading(true);
      setError(null);

      const data = await ragQuestionService.generateQuestions(
        null, // No chapter - generate from all chapters
        selectedSubject,
        5 // 5 questions per chapter
      );
console.log("Generated questions:", data);
      setQuestions(data.questions || []);
      setAnswers({});
      setStep("questions");
    } catch (err) {
      setError(
        "Failed to generate questions: " +
          (err.response?.data?.detail || err.message)
      );
      setStep("select");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleSubmitAssessment = async () => {
    // Check if all questions are answered
    const unansweredQuestions = questions.filter((q) => !answers[q.id]?.trim());

    if (unansweredQuestions.length > 0) {
      if (
        !window.confirm(
          `You have ${unansweredQuestions.length} unanswered questions. Submit anyway?`
        )
      ) {
        return;
      }
    }

    try {
      setLoading(true);
      setError(null);

      const answerArray = questions.map((q) => ({
        question_id: q.id,
        answer: answers[q.id] || "",
        chapter: q.chapter,
        question: q.question,
      }));

      const result = await ragQuestionService.submitAssessment(
        "All Chapters",
        selectedSubject,
        answerArray
      );

      setSubmittedAssessment(result);

      // Refresh user data to get updated levels
      try {
        await refreshUser();
      } catch (refreshError) {
        console.error("Failed to refresh user data:", refreshError);
      }

      // Redirect to evaluation page
      navigate(`/assessment-evaluation/${result.assessment_id}`);
    } catch (err) {
      setError(
        "Failed to submit assessment: " +
          (err.response?.data?.detail || err.message)
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStartNew = () => {
    setStep("select");
    setSelectedChapter("");
    setQuestions([]);
    setAnswers({});
    setSubmittedAssessment(null);
    setError(null);
  };

  const renderChapterSelection = () => (
    <div className="max-w-4xl mx-auto">
      <div
        className="rounded-lg shadow-md p-6"
        style={{ backgroundColor: "#F5EDE5" }}
      >
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Generate Assessment Questions
        </h2>

        {error && (
          <div
            className="mb-4 p-4 rounded-lg"
            style={{
              backgroundColor: "#FFEEF0",
              border: "1px solid #FFC9CC",
              color: "#991B1B",
            }}
          >
            {error}
          </div>
        )}

        {/* Subject Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Subject
          </label>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:border-transparent"
            style={{ borderColor: "#C9BDB3", focusRingColor: "#323232" }}
          >
            <option value="">Select a subject...</option>
            {subjects.map((subject) => (
              <option key={subject} value={subject}>
                {subject.charAt(0).toUpperCase() + subject.slice(1)}
              </option>
            ))}
          </select>
          <p className="mt-2 text-sm text-gray-600">
            The system will generate 5 questions from each chapter in the
            selected subject.
          </p>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerateQuestions}
          disabled={!selectedSubject || loading}
          className="w-full py-3 px-6 rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
        >
          {loading ? "Generating..." : "Generate Questions"}
        </button>
      </div>
    </div>
  );

  const renderQuestions = () => (
    <div className="max-w-4xl mx-auto">
      <div
        className="rounded-lg shadow-md p-6 mb-6"
        style={{ backgroundColor: "#F5EDE5" }}
      >
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {selectedSubject} - {selectedChapter}
            </h2>
            <p className="text-gray-600 mt-1">{questions.length} questions</p>
          </div>
          <button
            onClick={handleStartNew}
            className="px-4 py-2 font-medium transition-colors"
            style={{ color: "#323232" }}
          >
            Change Chapter
          </button>
        </div>

        {error && (
          <div
            className="mb-4 p-4 rounded-lg"
            style={{
              backgroundColor: "#FFEEF0",
              border: "1px solid #FFC9CC",
              color: "#991B1B",
            }}
          >
            {error}
          </div>
        )}

        {/* Questions */}
        <div className="space-y-6">
          {questions.map((question, index) => (
            <div
              key={question.id}
              className="pb-6 last:border-b-0"
              style={{ borderBottom: "1px solid #C9BDB3" }}
            >
              <div className="flex items-start gap-4">
                <div
                  className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-medium"
                  style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
                >
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-gray-800 font-medium mb-3">
                    {question.question}
                  </p>
                  <textarea
                    value={answers[question.id] || ""}
                    onChange={(e) =>
                      handleAnswerChange(question.id, e.target.value)
                    }
                    placeholder="Type your answer here..."
                    rows="4"
                    className="w-full px-4 py-3 rounded-lg resize-none focus:ring-2 focus:border-transparent"
                    style={{
                      border: "1px solid #C9BDB3",
                      backgroundColor: "#FFFFFF",
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Submit Button */}
        <div className="mt-8 flex justify-between items-center">
          <p className="text-gray-600">
            Answered: {Object.values(answers).filter((a) => a?.trim()).length} /{" "}
            {questions.length}
          </p>
          <button
            onClick={handleSubmitAssessment}
            disabled={loading}
            className="py-3 px-8 rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: "#6B8E23", color: "#FFFFFF" }}
          >
            {loading ? "Submitting..." : "Submit Assessment"}
          </button>
        </div>
      </div>
    </div>
  );

  const renderSubmitted = () => (
    <div className="max-w-2xl mx-auto">
      <div
        className="rounded-lg shadow-md p-8 text-center"
        style={{ backgroundColor: "#F5EDE5" }}
      >
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
          style={{ backgroundColor: "#E8F5E9" }}
        >
          <svg
            className="w-8 h-8"
            style={{ color: "#6B8E23" }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Assessment Submitted Successfully!
        </h2>

        <p className="text-gray-600 mb-6">
          Your answers have been saved and will be evaluated when the AI model
          is ready.
        </p>

        {submittedAssessment && (
          <div
            className="rounded-lg p-4 mb-6 text-left"
            style={{ backgroundColor: "#FFFFFF", border: "1px solid #C9BDB3" }}
          >
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Subject</p>
                <p className="font-medium">{submittedAssessment.subject}</p>
              </div>
              <div>
                <p className="text-gray-600">Chapter</p>
                <p className="font-medium">{submittedAssessment.chapter}</p>
              </div>
              <div>
                <p className="text-gray-600">Questions</p>
                <p className="font-medium">
                  {submittedAssessment.total_questions}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Status</p>
                <p className="font-medium capitalize">
                  {submittedAssessment.status.replace("_", " ")}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex gap-4 justify-center">
          <button
            onClick={handleStartNew}
            className="py-3 px-6 rounded-lg transition-colors font-medium"
            style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
          >
            Start New Assessment
          </button>
          <button
            onClick={() => (window.location.href = "/progress")}
            className="py-3 px-6 rounded-lg transition-colors font-medium"
            style={{ backgroundColor: "#E8DDD3", color: "#323232" }}
          >
            View Progress
          </button>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    if (step === "loading") {
      return (
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="text-center">
            <div
              className="w-16 h-16 border-4 border-t-transparent rounded-full animate-spin mx-auto mb-4"
              style={{ borderColor: "#323232", borderTopColor: "transparent" }}
            ></div>
            <p className="text-gray-600">Generating questions...</p>
          </div>
        </div>
      );
    }

    if (step === "questions") {
      return renderQuestions();
    }

    if (step === "submitted") {
      return renderSubmitted();
    }

    return renderChapterSelection();
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            AI-Powered Assessments
          </h1>
          <p className="text-gray-600 mt-2">
            Generate custom questions based on specific chapters and topics
          </p>
        </div>

        {renderContent()}
      </div>
    </DashboardLayout>
  );
};

export default RAGAssessmentPage;
