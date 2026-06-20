import { useEffect, useState } from "react";
import learningMaterialsService from "../../services/learningMaterials.service";
import Badge from "../common/Badge";
import Button from "../common/Button";
import Card from "../common/Card";

const LearningRoadmap = ({ subject }) => {
  const [materials, setMaterials] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [expandedChapter, setExpandedChapter] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMaterials();
  }, [subject]);

  const fetchMaterials = async () => {
    if (!subject) return;

    try {
      setLoading(true);
      setError(null);
      const data = await learningMaterialsService.getMyMaterials(subject);

      if (data && data.length > 0) {
        setMaterials(data[0]); // Get most recent
      } else {
        setMaterials(null);
      }
    } catch (err) {
      console.error("Error fetching materials:", err);
      setMaterials(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      setError(null);
      const data = await learningMaterialsService.generateMaterials(
        subject,
        false
      );
      setMaterials(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to generate learning plan. Complete assessments first."
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerate = async () => {
    try {
      setGenerating(true);
      setError(null);
      const data = await learningMaterialsService.generateMaterials(
        subject,
        true
      );
      setMaterials(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to regenerate plan");
    } finally {
      setGenerating(false);
    }
  };

  const getWeaknessColor = (level) => {
    switch (level) {
      case "severe":
        return "#7C2D12";
      case "moderate":
        return "#78350F";
      case "mild":
        return "#065F46";
      default:
        return "#5A5A5A";
    }
  };

  const getWeaknessLabel = (level) => {
    switch (level) {
      case "severe":
        return "Critical";
      case "moderate":
        return "Needs Focus";
      case "mild":
        return "Minor Gap";
      default:
        return "Good";
    }
  };

  if (loading) {
    return (
      <div
        className="text-center py-8 rounded-2xl"
        style={{ backgroundColor: "#F5EDE5", border: "1px solid #C9BDB3" }}
      >
        <div
          className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto"
          style={{ borderColor: "#323232" }}
        ></div>
        <p className="mt-4" style={{ color: "#5A5A5A" }}>
          Loading learning plan...
        </p>
      </div>
    );
  }

  if (!materials) {
    return (
      <Card
        title={
          <div className="flex items-center gap-2">
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
            <span>Your Personalized Learning Plan</span>
          </div>
        }
      >
        <div className="text-center py-8">
          <p className="text-gray-600 mb-4">
            No learning plan available yet for {subject}.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Complete assessments to receive AI-generated study recommendations.
          </p>
          <Button onClick={handleGenerate} disabled={generating}>
            {generating ? "Generating..." : "Generate Learning Plan"}
          </Button>
          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
        </div>
      </Card>
    );
  }

  const content = materials.content;
  const chapters = content.chapters || [];
  const recommendations = content.global_recommendations || {};

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card
        title={
          <div className="flex items-center gap-2">
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
            <span>{subject} Learning Plan</span>
          </div>
        }
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              className="text-center p-3 rounded-lg"
              style={{
                backgroundColor: "#F5EDE5",
                border: "1px solid #C9BDB3",
              }}
            >
              <div className="text-2xl font-bold" style={{ color: "#8B7355" }}>
                {recommendations.weekly_study_hours || 6}h
              </div>
              <div className="text-xs" style={{ color: "#5A5A5A" }}>
                Per Week
              </div>
            </div>
            <div
              className="text-center p-3 rounded-lg"
              style={{
                backgroundColor: "#F5EDE5",
                border: "1px solid #C9BDB3",
              }}
            >
              <div className="text-2xl font-bold" style={{ color: "#8B7355" }}>
                {recommendations.minimum_duration_weeks || 6}
              </div>
              <div className="text-xs" style={{ color: "#5A5A5A" }}>
                Weeks
              </div>
            </div>
            <div
              className="text-center p-3 rounded-lg"
              style={{
                backgroundColor: "#F5EDE5",
                border: "1px solid #C9BDB3",
              }}
            >
              <div className="text-2xl font-bold" style={{ color: "#8B7355" }}>
                {chapters.length}
              </div>
              <div className="text-xs" style={{ color: "#5A5A5A" }}>
                Chapters
              </div>
            </div>
            <div
              className="text-center p-3 rounded-lg"
              style={{
                backgroundColor: "#F5EDE5",
                border: "1px solid #C9BDB3",
              }}
            >
              <div className="text-2xl font-bold" style={{ color: "#7C2D12" }}>
                {chapters.filter((c) => c.weakness_level === "severe").length}
              </div>
              <div className="text-xs" style={{ color: "#5A5A5A" }}>
                Critical
              </div>
            </div>
          </div>

          {recommendations.notes && (
            <div
              className="p-3 rounded border-l-4"
              style={{ backgroundColor: "#F5EDE5", borderColor: "#8B7355" }}
            >
              <p className="text-sm" style={{ color: "#323232" }}>
                {recommendations.notes}
              </p>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={handleRegenerate}
              disabled={generating}
            >
              <div className="flex items-center gap-2">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                <span>
                  {generating ? "Regenerating..." : "Regenerate Plan"}
                </span>
              </div>
            </Button>
          </div>
        </div>
      </Card>

      {/* Chapter Cards */}
      <div className="space-y-4">
        {chapters
          .sort((a, b) => (b.priority || 3) - (a.priority || 3))
          .map((chapter, index) => (
            <Card key={index} hoverable>
              <div
                className="cursor-pointer"
                onClick={() =>
                  setExpandedChapter(expandedChapter === index ? null : index)
                }
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {chapter.chapter_name}
                    </h3>
                    <div className="flex gap-2 items-center">
                      <Badge
                        variant="warning"
                        size="sm"
                        style={{
                          backgroundColor: `${getWeaknessColor(
                            chapter.weakness_level
                          )}20`,
                          color: getWeaknessColor(chapter.weakness_level),
                        }}
                      >
                        {getWeaknessLabel(chapter.weakness_level)}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        Priority: {chapter.priority || 3}/5
                      </span>
                      <span className="text-xs text-gray-500">
                        ~{chapter.estimated_time_hours || 4}h
                      </span>
                    </div>
                  </div>
                  <span className="text-gray-400">
                    {expandedChapter === index ? "▼" : "▶"}
                  </span>
                </div>

                {/* Expanded Content */}
                {expandedChapter === index && (
                  <div className="mt-4 space-y-4 border-t pt-4">
                    {/* Prerequisites */}
                    {chapter.prerequisites &&
                      chapter.prerequisites.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700 mb-2">
                            Prerequisites
                          </h4>
                          <div className="space-y-2">
                            {chapter.prerequisites.map((prereq, i) => (
                              <div
                                key={i}
                                className="p-2 bg-gray-50 rounded text-sm"
                              >
                                <div className="font-medium">
                                  {prereq.concept}
                                </div>
                                <div className="text-xs text-gray-600">
                                  {prereq.why}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    {/* Roadmap Steps */}
                    {chapter.roadmap_steps &&
                      chapter.roadmap_steps.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700 mb-2">
                            Study Roadmap
                          </h4>
                          <div className="space-y-2">
                            {chapter.roadmap_steps.map((step, i) => (
                              <div
                                key={i}
                                className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded"
                              >
                                <div
                                  className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                                  style={{
                                    backgroundColor: "#DDD0C8",
                                    color: "#323232",
                                  }}
                                >
                                  {step.step_number}
                                </div>
                                <div className="flex-1">
                                  <div className="text-sm">
                                    {step.objective}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    ~{step.estimated_time_minutes || 30} min
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    {/* Resources */}
                    {chapter.resources && chapter.resources.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm text-gray-700 mb-2">
                          Recommended Resources
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {chapter.resources.map((resource, i) => (
                            <a
                              key={i}
                              href={resource.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-3 border rounded-lg hover:shadow-sm transition-all"
                              style={{ borderColor: "#C9BDB3" }}
                              onMouseEnter={(e) =>
                                (e.currentTarget.style.borderColor = "#8B7355")
                              }
                              onMouseLeave={(e) =>
                                (e.currentTarget.style.borderColor = "#C9BDB3")
                              }
                            >
                              <div className="flex items-start justify-between mb-1">
                                <div className="font-medium text-sm">
                                  {resource.title}
                                </div>
                                <Badge variant="info" size="sm">
                                  {resource.type}
                                </Badge>
                              </div>
                              <p className="text-xs text-gray-600 mb-2">
                                {resource.description}
                              </p>
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">
                                  {resource.level}
                                </span>
                                <span className="text-gray-500">
                                  {resource.estimated_time_minutes || 15} min
                                </span>
                              </div>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
      </div>
    </div>
  );
};

export default LearningRoadmap;
