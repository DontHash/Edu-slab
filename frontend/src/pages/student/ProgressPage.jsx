import { useEffect, useState } from "react";
import Card from "../../components/common/Card";
import DashboardLayout from "../../components/layout/DashboardLayout";
import ragQuestionService from "../../services/ragQuestion.service";
import useAuthStore from "../../store/authStore";

const ProgressPage = () => {
  const { user } = useAuthStore();
  const [subjectsProgress, setSubjectsProgress] = useState({});
  const [selectedSubject, setSelectedSubject] = useState("maths");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        setLoading(true);

        // Fetch RAG-based subject progress
        const ragProgress = await ragQuestionService.getAllSubjectsProgress();
        setSubjectsProgress(ragProgress.subjects_progress || {});
      } catch (err) {
        console.error("Error fetching progress:", err);
        setError(err.message || "Failed to load progress data");
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, []);

  const currentSubjectData = subjectsProgress[selectedSubject];

  return (
    <DashboardLayout user={user}>
      <div>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: "#323232" }}>
            My Progress
          </h1>
          <p className="text-gray-600">
            Track your performance and identify areas for improvement
          </p>
        </div>

        {loading && (
          <div className="text-center py-12">
            <div
              className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto"
              style={{ borderColor: "#323232" }}
            ></div>
            <p className="mt-4 text-gray-600">Loading your progress...</p>
          </div>
        )}

        {error && (
          <div
            className="rounded-lg p-4 mb-6"
            style={{ backgroundColor: "#FFEEF0", border: "1px solid #FFC9CC" }}
          >
            <p style={{ color: "#DC2626" }}>{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-6">
            {/* Subject Tabs */}
            <div className="flex flex-wrap gap-3 mb-6">
              {["maths", "science", "english"].map((subject) => (
                <button
                  key={subject}
                  onClick={() => setSelectedSubject(subject)}
                  className="px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                  style={{
                    backgroundColor:
                      selectedSubject === subject ? "#323232" : "#F5EDE5",
                    color: selectedSubject === subject ? "#F5EDE5" : "#5A5A5A",
                  }}
                >
                  <div className="flex items-center gap-2">
                    <span>
                      {subject.charAt(0).toUpperCase() + subject.slice(1)}
                    </span>
                    {subjectsProgress[subject]?.has_data && (
                      <span
                        className="text-xs px-2 py-1 rounded-full font-bold"
                        style={{
                          backgroundColor:
                            selectedSubject === subject ? "#6B8E23" : "#E8DDD3",
                          color:
                            selectedSubject === subject ? "#FFFFFF" : "#323232",
                        }}
                      >
                        {subjectsProgress[subject].overall_score}%
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </div>

            {/* Subject Progress Content */}
            {currentSubjectData?.has_data ? (
              <div className="space-y-6">
                {/* Overall Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div
                    className="p-6 rounded-lg border"
                    style={{
                      backgroundColor: "#F5EDE5",
                      borderColor: "#C9BDB3",
                    }}
                  >
                    <h3 className="text-xs font-semibold uppercase tracking-wide mb-2 text-gray-600">
                      Overall Score
                    </h3>
                    <p
                      className="text-3xl font-bold mb-2"
                      style={{ color: "#323232" }}
                    >
                      {currentSubjectData.overall_score}%
                    </p>
                    <div
                      className="h-1.5 rounded-full overflow-hidden"
                      style={{ backgroundColor: "#E8DDD3" }}
                    >
                      <div
                        className="h-full transition-all duration-500"
                        style={{
                          width: `${currentSubjectData.overall_score}%`,
                          backgroundColor: "#6B8E23",
                        }}
                      ></div>
                    </div>
                  </div>
                  <div
                    className="p-6 rounded-lg border"
                    style={{
                      backgroundColor: "#F5EDE5",
                      borderColor: "#C9BDB3",
                    }}
                  >
                    <h3 className="text-xs font-semibold uppercase tracking-wide mb-2 text-gray-600">
                      Estimated Level
                    </h3>
                    <p
                      className="text-3xl font-bold"
                      style={{ color: "#323232" }}
                    >
                      Grade {currentSubjectData.estimated_grade_level || "N/A"}
                    </p>
                  </div>
                  <div
                    className="p-6 rounded-lg border"
                    style={{
                      backgroundColor: "#F5EDE5",
                      borderColor: "#C9BDB3",
                    }}
                  >
                    <h3 className="text-xs font-semibold uppercase tracking-wide mb-2 text-gray-600">
                      Last Assessed
                    </h3>
                    <p
                      className="text-xl font-bold"
                      style={{ color: "#323232" }}
                    >
                      {new Date(
                        currentSubjectData.assessed_at
                      ).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </p>
                  </div>
                </div>

                {/* Strengths */}
                {currentSubjectData.strengths &&
                  currentSubjectData.strengths.length > 0 && (
                    <Card title="Your Strengths">
                      <p className="text-sm text-gray-600 mb-4">
                        Chapters where you scored 85% or above
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-2">
                        {currentSubjectData.strengths.map((strength, idx) => (
                          <div
                            key={idx}
                            className="p-4 rounded-lg border-l-4"
                            style={{
                              backgroundColor: "#F5EDE5",
                              borderLeftColor: "#6B8E23",
                            }}
                          >
                            <div className="flex justify-between items-start mb-2">
                              <h4
                                className="font-semibold text-sm"
                                style={{ color: "#323232" }}
                              >
                                {strength.chapter}
                              </h4>
                              <span
                                className="text-lg font-bold"
                                style={{ color: "#6B8E23" }}
                              >
                                {strength.accuracy}%
                              </span>
                            </div>
                            <p className="text-xs text-gray-600">
                              Score: {strength.score}/10
                            </p>
                          </div>
                        ))}
                      </div>
                    </Card>
                  )}

                {/* Areas to Improve */}
                {currentSubjectData.areas_to_improve &&
                  currentSubjectData.areas_to_improve.length > 0 && (
                    <Card title="Areas to Improve">
                      <p className="text-sm text-gray-600 mb-4">
                        Chapters where you scored between 50% and 85%
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-2">
                        {currentSubjectData.areas_to_improve.map(
                          (area, idx) => (
                            <div
                              key={idx}
                              className="p-4 rounded-lg border-l-4"
                              style={{
                                backgroundColor: "#FFF8E1",
                                borderLeftColor: "#F59E0B",
                              }}
                            >
                              <div className="flex justify-between items-start mb-2">
                                <h4
                                  className="font-semibold text-sm"
                                  style={{ color: "#323232" }}
                                >
                                  {area.chapter}
                                </h4>
                                <span
                                  className="text-lg font-bold"
                                  style={{ color: "#F59E0B" }}
                                >
                                  {area.accuracy}%
                                </span>
                              </div>
                              <p className="text-xs text-gray-600">
                                Score: {area.score}/10 • {area.weakness_level}
                              </p>
                            </div>
                          )
                        )}
                      </div>
                    </Card>
                  )}

                {/* Critical Weaknesses */}
                {currentSubjectData.critical_weaknesses &&
                  currentSubjectData.critical_weaknesses.length > 0 && (
                    <Card title="Critical Weaknesses">
                      <p className="text-sm text-gray-600 mb-4">
                        Chapters where you scored below 50% - these need
                        immediate attention
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-2">
                        {currentSubjectData.critical_weaknesses.map(
                          (weakness, idx) => (
                            <div
                              key={idx}
                              className="p-4 rounded-lg border-l-4"
                              style={{
                                backgroundColor: "#FFEEF0",
                                borderLeftColor: "#DC2626",
                              }}
                            >
                              <div className="flex justify-between items-start mb-2">
                                <h4
                                  className="font-semibold text-sm"
                                  style={{ color: "#323232" }}
                                >
                                  {weakness.chapter}
                                </h4>
                                <span
                                  className="text-lg font-bold"
                                  style={{ color: "#DC2626" }}
                                >
                                  {weakness.accuracy}%
                                </span>
                              </div>
                              <p className="text-xs text-gray-600 mb-2">
                                Score: {weakness.score}/10
                              </p>
                              <a
                                href="/resources"
                                className="text-xs font-medium"
                                style={{ color: "#323232" }}
                              >
                                Find study resources →
                              </a>
                            </div>
                          )
                        )}
                      </div>
                    </Card>
                  )}

                {/* Learning Gaps Summary */}
                {currentSubjectData.learning_gaps &&
                  currentSubjectData.learning_gaps.length > 0 && (
                    <Card title="Detailed Analysis">
                      <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                        {currentSubjectData.learning_gaps.map((gap, idx) => (
                          <div
                            key={idx}
                            className="p-4 rounded-lg border"
                            style={{
                              backgroundColor: "#F5EDE5",
                              borderColor: "#C9BDB3",
                            }}
                          >
                            <p className="text-sm text-gray-800 leading-relaxed">
                              {gap}
                            </p>
                          </div>
                        ))}
                      </div>
                    </Card>
                  )}
              </div>
            ) : (
              <div
                className="text-center py-12 rounded-lg"
                style={{ backgroundColor: "#F5EDE5" }}
              >
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                  style={{ backgroundColor: "#E8DDD3" }}
                >
                  <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="#5A5A5A"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <h3
                  className="text-lg font-semibold mb-2"
                  style={{ color: "#323232" }}
                >
                  No{" "}
                  {selectedSubject.charAt(0).toUpperCase() +
                    selectedSubject.slice(1)}{" "}
                  Data Yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Take an assessment to see your progress
                </p>
                <a
                  href="/assessment"
                  className="inline-block px-6 py-2 rounded-lg font-medium transition-colors"
                  style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
                >
                  Take Assessment
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ProgressPage;
