import { useEffect, useState } from "react";
import ragQuestionService from "../../services/ragQuestion.service";

const SubjectProgressChart = () => {
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animationTriggered, setAnimationTriggered] = useState(false);
  const [activeSubject, setActiveSubject] = useState("maths");

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const data = await ragQuestionService.getAllSubjectsProgress();
        console.log("[DEBUG] Raw API response:", data);

        // Process data - strengths array contains chapters with 100% accuracy
        const processedData = {};
        for (const [subject, subjectData] of Object.entries(
          data.subjects_progress
        )) {
          processedData[subject] = {
            ...subjectData,
            // Use strengths array from API (chapters with perfect scores)
            strong_areas: subjectData.strengths || [],
          };
          console.log(`[DEBUG] Processed ${subject}:`, processedData[subject]);
        }

        setProgressData(processedData);
        setLoading(false);
        // Trigger animation after data loads
        setTimeout(() => setAnimationTriggered(true), 100);
      } catch (error) {
        console.error("Failed to load progress:", error);
        setLoading(false);
      }
    };

    fetchProgress();
  }, []);

  // Reset animation when subject changes
  useEffect(() => {
    setAnimationTriggered(false);
    setTimeout(() => setAnimationTriggered(true), 100);
  }, [activeSubject]);

  if (loading) {
    return (
      <div className="text-center py-8">
        <div
          className="inline-block animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: "#323232" }}
        ></div>
      </div>
    );
  }

  if (!progressData) {
    return (
      <div
        className="text-center py-8 rounded-xl"
        style={{ backgroundColor: "#F5EDE5", border: "1px solid #C9BDB3" }}
      >
        <p style={{ color: "#5A5A5A" }}>No progress data available</p>
      </div>
    );
  }

  const subjects = [
    {
      key: "maths",
      label: "Mathematics",
      color: "#8B7355",
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
          />
        </svg>
      ),
    },
    {
      key: "science",
      label: "Science",
      color: "#A0826D",
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
          />
        </svg>
      ),
    },
    {
      key: "english",
      label: "English",
      color: "#B8956A",
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      ),
    },
  ];

  const currentSubject = subjects.find((s) => s.key === activeSubject);
  const currentData = progressData[activeSubject];

  console.log("[DEBUG] Current subject:", activeSubject);
  console.log("[DEBUG] Current data:", currentData);
  console.log("[DEBUG] Has data?", currentData?.has_data);

  return (
    <div className="space-y-6">
      {/* Subject Tabs */}
      <div className="flex gap-3">
        {subjects.map((subject) => (
          <button
            key={subject.key}
            onClick={() => setActiveSubject(subject.key)}
            className="flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all shadow-sm"
            style={
              activeSubject === subject.key
                ? {
                    backgroundColor: "#323232",
                    color: "#DDD0C8",
                  }
                : {
                    backgroundColor: "#F5EDE5",
                    color: "#5A5A5A",
                    border: "1px solid #C9BDB3",
                  }
            }
          >
            {subject.icon}
            <span>{subject.label}</span>
          </button>
        ))}
      </div>

      {/* Subject Content */}
      {currentData && currentData.has_data ? (
        <div className="space-y-6">
          {/* Overall Performance Card */}
          <div
            className="rounded-2xl p-6 shadow-sm border"
            style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div
                  className="p-3 rounded-lg"
                  style={{ backgroundColor: "#DDD0C8" }}
                >
                  {currentSubject.icon}
                </div>
                <div>
                  <h3
                    className="text-xl font-bold"
                    style={{ color: "#323232" }}
                  >
                    {currentSubject.label}
                  </h3>
                  <p className="text-sm" style={{ color: "#5A5A5A" }}>
                    Overall Performance
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div
                  className="text-4xl font-bold"
                  style={{ color: currentSubject.color }}
                >
                  {currentData.overall_score}%
                </div>
                <p className="text-sm mt-1" style={{ color: "#5A5A5A" }}>
                  Grade Level: {currentData.estimated_grade_level || "N/A"}
                </p>
              </div>
            </div>

            {/* Main Progress Bar */}
            <div
              className="relative h-4 rounded-full overflow-hidden mb-4"
              style={{ backgroundColor: "#E8DDD3" }}
            >
              <div
                className="absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ease-out"
                style={{
                  width: animationTriggered
                    ? `${currentData.overall_score}%`
                    : "0%",
                  backgroundColor: currentSubject.color,
                  boxShadow: `0 0 15px ${currentSubject.color}60`,
                }}
              >
                <div
                  className="absolute inset-0 opacity-30"
                  style={{
                    background:
                      "linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)",
                    animation: "shimmer 2s infinite",
                  }}
                ></div>
              </div>
            </div>

            {/* Performance Label */}
            <div className="text-center">
              <span
                className="inline-block px-4 py-2 rounded-full text-sm font-semibold"
                style={{
                  backgroundColor:
                    currentData.overall_percentage >= 80
                      ? "#D4EDDA"
                      : currentData.overall_percentage >= 60
                      ? "#FFF3CD"
                      : currentData.overall_percentage >= 40
                      ? "#F8D7DA"
                      : "#F5EDE5",
                  color:
                    currentData.overall_percentage >= 80
                      ? "#155724"
                      : currentData.overall_percentage >= 60
                      ? "#856404"
                      : currentData.overall_percentage >= 40
                      ? "#721C24"
                      : "#5A5A5A",
                }}
              >
                {currentData.overall_percentage >= 80
                  ? "🌟 Excellent Performance"
                  : currentData.overall_percentage >= 60
                  ? "✨ Good Progress"
                  : currentData.overall_percentage >= 40
                  ? "💪 Keep Working"
                  : "📈 Needs More Practice"}
              </span>
            </div>
          </div>

          {/* Critical Weaknesses */}
          {currentData.critical_weaknesses &&
            currentData.critical_weaknesses.length > 0 && (
              <div
                className="rounded-2xl p-6 shadow-sm border"
                style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
              >
                <h3
                  className="text-lg font-semibold mb-4 flex items-center gap-2"
                  style={{ color: "#7C2D12" }}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  Critical Weaknesses - Needs Immediate Attention
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentData.critical_weaknesses.map((weakness, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg border"
                      style={{
                        backgroundColor: "#FFFFFF",
                        borderColor: "#C9BDB3",
                      }}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4
                          className="font-semibold text-sm flex-1"
                          style={{ color: "#7C2D12" }}
                        >
                          {weakness.chapter}
                        </h4>
                        <span
                          className="text-lg font-bold ml-2"
                          style={{ color: "#92400E" }}
                        >
                          {weakness.accuracy}%
                        </span>
                      </div>
                      <p className="text-sm" style={{ color: "#5A5A5A" }}>
                        Score: {weakness.score}/10
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Areas to Improve */}
          {currentData.areas_to_improve &&
            currentData.areas_to_improve.length > 0 && (
              <div
                className="rounded-2xl p-6 shadow-sm border"
                style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
              >
                <h3
                  className="text-lg font-semibold mb-4 flex items-center gap-2"
                  style={{ color: "#78350F" }}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                    />
                  </svg>
                  Areas to Improve
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {currentData.areas_to_improve.map((area, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg border"
                      style={{
                        backgroundColor: "#FFFFFF",
                        borderColor: "#C9BDB3",
                      }}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4
                          className="font-semibold text-sm flex-1"
                          style={{ color: "#78350F" }}
                        >
                          {area.chapter}
                        </h4>
                        <span
                          className="text-lg font-bold ml-2"
                          style={{ color: "#92400E" }}
                        >
                          {area.accuracy}%
                        </span>
                      </div>
                      <p className="text-xs" style={{ color: "#5A5A5A" }}>
                        Score: {area.score}/10
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Areas Where You Excel */}
          {currentData.strong_areas && currentData.strong_areas.length > 0 && (
            <div
              className="rounded-2xl p-6 shadow-sm border"
              style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
            >
              <h3
                className="text-lg font-semibold mb-4 flex items-center gap-2"
                style={{ color: "#065F46" }}
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                  />
                </svg>
                Areas Where You Excel (100% Accuracy)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {currentData.strong_areas.map((area, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-lg border"
                    style={{
                      backgroundColor: "#FFFFFF",
                      borderColor: "#C9BDB3",
                    }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4
                        className="font-semibold text-sm flex-1"
                        style={{ color: "#065F46" }}
                      >
                        {typeof area === "string" ? area : area.chapter}
                      </h4>
                      <span
                        className="text-lg font-bold ml-2"
                        style={{ color: "#047857" }}
                      >
                        100%
                      </span>
                    </div>
                    <p className="text-xs" style={{ color: "#5A5A5A" }}>
                      Perfect Score
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chapter Breakdown */}
          {currentData.chapter_breakdown &&
            currentData.chapter_breakdown.length > 0 && (
              <div
                className="rounded-2xl p-6 shadow-sm border"
                style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
              >
                <h3
                  className="text-lg font-semibold mb-4 flex items-center gap-2"
                  style={{ color: "#323232" }}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  Chapter-wise Performance
                </h3>
                <div className="space-y-4">
                  {currentData.chapter_breakdown.map((chapter, idx) => (
                    <div key={idx} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4
                          className="font-medium"
                          style={{ color: "#323232" }}
                        >
                          {chapter.chapter}
                        </h4>
                        <div className="flex items-center gap-3">
                          <span
                            className="text-sm"
                            style={{ color: "#5A5A5A" }}
                          >
                            {chapter.correct}/{chapter.total} questions
                          </span>
                          <span
                            className="text-lg font-bold min-w-[60px] text-right"
                            style={{
                              color:
                                chapter.percentage >= 70
                                  ? currentSubject.color
                                  : chapter.percentage >= 40
                                  ? "#F59E0B"
                                  : "#DC2626",
                            }}
                          >
                            {chapter.percentage}%
                          </span>
                        </div>
                      </div>

                      {/* Chapter Progress Bar */}
                      <div
                        className="relative h-2.5 rounded-full overflow-hidden"
                        style={{ backgroundColor: "#E8DDD3" }}
                      >
                        <div
                          className="absolute top-0 left-0 h-full rounded-full transition-all duration-700"
                          style={{
                            width: animationTriggered
                              ? `${chapter.percentage}%`
                              : "0%",
                            backgroundColor:
                              chapter.percentage >= 70
                                ? currentSubject.color
                                : chapter.percentage >= 40
                                ? "#F59E0B"
                                : "#DC2626",
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      ) : (
        <div
          className="text-center py-16 rounded-2xl shadow-sm border"
          style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
        >
          <span className="text-5xl mb-4 block">{currentSubject.icon}</span>
          <h3
            className="text-xl font-semibold mb-2"
            style={{ color: "#323232" }}
          >
            No {currentSubject.label} Data Yet
          </h3>
          <p className="text-sm mb-4" style={{ color: "#5A5A5A" }}>
            Complete your {currentSubject.label} assessment to see your progress
            here
          </p>
          <a
            href="/assessment"
            className="inline-block px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md"
            style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
          >
            Take Assessment
          </a>
        </div>
      )}

      <style>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
};

export default SubjectProgressChart;
