import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../services/api";

const AssessmentEvaluationPage = () => {
  const { assessmentId } = useParams();
  const navigate = useNavigate();

  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    loadEvaluation();
  }, [assessmentId]);

  const loadEvaluation = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to get existing evaluation
      const response = await api.get(
        `/rag/evaluate-assessment/${assessmentId}`
      );
      setEvaluation(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        // No evaluation exists yet - auto-trigger it
        handleEvaluate();
      } else {
        setError("Failed to load evaluation");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async () => {
    try {
      setEvaluating(true);
      setError(null);

      const response = await api.post(
        `/rag/evaluate-assessment/${assessmentId}`
      );
      setEvaluation(response.data);

      // Show success message with updated levels
      alert("Assessment evaluated successfully! View your topic report and learning roadmap.");
    } catch (err) {
      setError(
        "Failed to evaluate assessment: " +
          (err.response?.data?.detail || err.message)
      );
    } finally {
      setEvaluating(false);
    }
  };

  const getWeaknessColor = (level) => {
    switch (level) {
      case "none":
        return "text-green-800";
      case "mild":
        return "text-yellow-800";
      case "moderate":
        return "text-orange-800";
      case "severe":
        return "text-red-800";
      default:
        return "text-gray-800";
    }
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 85) return "#6B8E23";
    if (percentage >= 70) return "#F59E0B";
    if (percentage >= 50) return "#FB923C";
    return "#DC2626";
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <div
            className="inline-block animate-spin rounded-full h-12 w-12 border-b-2"
            style={{ borderColor: "#323232" }}
          ></div>
          <p className="mt-4 text-gray-600">Loading evaluation...</p>
        </div>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div
          className="rounded-lg shadow-md p-6 text-center"
          style={{ backgroundColor: "#F5EDE5" }}
        >
          <h2 className="text-2xl font-bold mb-4" style={{ color: "#323232" }}>
            Assessment Not Evaluated Yet
          </h2>
          <p className="text-gray-600 mb-6">
            Click the button below to evaluate this assessment using AI.
          </p>
          <button
            onClick={handleEvaluate}
            disabled={evaluating}
            className="px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
          >
            {evaluating ? "Evaluating..." : "Evaluate Assessment"}
          </button>
          {error && (
            <div
              className="mt-4 p-4 rounded-lg"
              style={{ backgroundColor: "#FFEEF0", color: "#DC2626" }}
            >
              {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  const { chapter_analysis, overall_analysis } = evaluation;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate("/dashboard")}
          className="font-medium transition-colors"
          style={{ color: "#323232" }}
        >
          ← Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold" style={{ color: "#323232" }}>
          Assessment Evaluation
        </h1>
      </div>

      {/* Overall Score Card */}
      <div
        className="rounded-lg shadow-lg p-8 mb-6 text-white"
        style={{ background: "linear-gradient(to right, #323232, #5A5A5A)" }}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-gray-300 text-sm mb-1">Final Score</p>
            <p className="text-5xl font-bold">
              {overall_analysis?.final_score_out_of_100 || 0}
            </p>
            <p className="text-gray-300 mt-1">out of 100</p>
          </div>
          <div>
            <p className="text-gray-300 text-sm mb-1">Estimated Grade Level</p>
            <p className="text-5xl font-bold">
              Grade {overall_analysis?.estimated_student_grade_level || "-"}
            </p>
          </div>
          <div>
            <p className="text-gray-300 text-sm mb-1">Strongest Chapters</p>
            {overall_analysis?.strongest_chapters?.map((chapter, idx) => (
              <p key={idx} className="text-lg font-semibold">
                ✓ {chapter}
              </p>
            ))}
          </div>
        </div>
      </div>

      {/* Learning Gaps */}
      {overall_analysis?.learning_gap_summary &&
        overall_analysis.learning_gap_summary.length > 0 && (
          <div
            className="border-l-4 p-6 mb-6 rounded-lg"
            style={{ backgroundColor: "#FFF8E1", borderLeftColor: "#F59E0B" }}
          >
            <h2 className="text-xl font-bold mb-3" style={{ color: "#B45309" }}>
              Learning Gaps Identified
            </h2>
            <div className="space-y-2">
              {overall_analysis.learning_gap_summary.map((gap, idx) => (
                <p key={idx} className="text-gray-800">
                  • {gap}
                </p>
              ))}
            </div>
          </div>
        )}

      {/* Weakest Chapters Alert */}
      {overall_analysis?.weakest_chapters &&
        overall_analysis.weakest_chapters.length > 0 && (
          <div
            className="border-l-4 p-6 mb-6 rounded-lg"
            style={{ backgroundColor: "#FFEEF0", borderLeftColor: "#DC2626" }}
          >
            <h2 className="text-xl font-bold mb-3" style={{ color: "#991B1B" }}>
              Areas Needing Improvement
            </h2>
            <div className="flex flex-wrap gap-2">
              {overall_analysis.weakest_chapters.map((chapter, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-full text-sm font-medium"
                  style={{ backgroundColor: "#FFC9CC", color: "#991B1B" }}
                >
                  {chapter}
                </span>
              ))}
            </div>
          </div>
        )}

      {/* Chapter-wise Analysis */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          Chapter-wise Performance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[36rem] overflow-y-auto pr-2">
          {Object.entries(chapter_analysis || {}).map(([chapter, data]) => (
            <div
              key={chapter}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <h3 className="font-semibold text-gray-800 mb-2">{chapter}</h3>

              {/* Progress bar */}
              <div
                className="w-full rounded-full h-2 mb-2"
                style={{ backgroundColor: "#E8DDD3" }}
              >
                <div
                  className="h-2 rounded-full"
                  style={{
                    width: `${data.accuracy_percentage}%`,
                    backgroundColor:
                      data.accuracy_percentage >= 85
                        ? "#6B8E23"
                        : data.accuracy_percentage >= 70
                        ? "#F59E0B"
                        : data.accuracy_percentage >= 50
                        ? "#FB923C"
                        : "#DC2626",
                  }}
                ></div>
              </div>

              <div className="flex justify-between items-center mb-2">
                <span
                  className="text-2xl font-bold"
                  style={{ color: getScoreColor(data.accuracy_percentage) }}
                >
                  {data.accuracy_percentage}%
                </span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${getWeaknessColor(
                    data.weakness_level
                  )}`}
                  style={{
                    backgroundColor:
                      data.weakness_level === "none"
                        ? "#F0F9E8"
                        : data.weakness_level === "mild"
                        ? "#FFF8E1"
                        : data.weakness_level === "moderate"
                        ? "#FFF3E0"
                        : "#FFEEF0",
                  }}
                >
                  {data.weakness_level}
                </span>
              </div>

              <div className="text-sm text-gray-600 space-y-1">
                <div className="flex justify-between">
                  <span>Correct:</span>
                  <span className="font-medium" style={{ color: "#6B8E23" }}>
                    {data.correct}/{data.total_questions}
                  </span>
                </div>
                {data.partial > 0 && (
                  <div className="flex justify-between">
                    <span>Partial:</span>
                    <span className="font-medium" style={{ color: "#F59E0B" }}>
                      {data.partial}
                    </span>
                  </div>
                )}
                {data.incorrect > 0 && (
                  <div className="flex justify-between">
                    <span>Incorrect:</span>
                    <span className="font-medium" style={{ color: "#DC2626" }}>
                      {data.incorrect}
                    </span>
                  </div>
                )}
                <div className="flex justify-between pt-1 border-t">
                  <span>Score:</span>
                  <span className="font-bold">
                    {data.chapter_score_out_of_10}/10
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex gap-4">
        <button
          onClick={() => navigate("/assessment")}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Take Another Assessment
        </button>
        <button
          onClick={() => window.print()}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          Print Report
        </button>
      </div>
    </div>
  );
};

export default AssessmentEvaluationPage;
