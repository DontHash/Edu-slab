import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ragQuestionService from "../../services/ragQuestion.service";
import Badge from "../common/Badge";
import Card from "../common/Card";

const LearningRoadmap = ({ subject }) => {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedChapter, setExpandedChapter] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRoadmap();
  }, [subject]);

  const fetchRoadmap = async () => {
    if (!subject) return;
    try {
      setLoading(true);
      setError(null);
      const data = await ragQuestionService.getLearningRoadmap(subject);
      if (data?.has_data) setRoadmap(data);
      else {
        setRoadmap(null);
        setError(data?.message || null);
      }
    } catch (err) {
      setRoadmap(null);
      setError(err.response?.data?.detail || "Could not load roadmap.");
    } finally {
      setLoading(false);
    }
  };

  const weaknessBadge = (level) => {
    if (level === "severe") return "danger";
    if (level === "moderate") return "warning";
    return "info";
  };

  if (loading) {
    return (
      <div className="flex min-h-[30vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!roadmap) {
    return (
      <Card title="Personalized roadmap">
        <div className="py-8 text-center">
          <p className="text-muted mb-4">
            {error || "Complete a diagnostic assessment to unlock your study plan."}
          </p>
          <Link to="/assessment" className="ds-btn-primary inline-flex">
            Take assessment
          </Link>
        </div>
      </Card>
    );
  }

  const chapters = roadmap.content?.chapters || [];
  const recommendations = roadmap.content?.global_recommendations || {};
  const allResources = roadmap.all_resources || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <Card
        title={
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span>{subject} roadmap</span>
            <div className="flex items-center gap-2">
              {roadmap.evaluation_method && (
                <Badge variant="info">{roadmap.evaluation_method.replace(/_/g, " ")}</Badge>
              )}
              {roadmap.assessment_id && (
              <Link
                to={`/assessment-evaluation/${roadmap.assessment_id}`}
                className="text-sm font-semibold text-primary hover:text-primary-dark"
              >
                Full report →
              </Link>
              )}
            </div>
          </div>
        }
      >
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            { label: "Latest score", value: roadmap.overall_score ?? "—" },
            { label: "Proficiency", value: roadmap.proficiency_label || "—" },
            { label: "Topics", value: chapters.length },
            { label: "Critical", value: chapters.filter((c) => c.weakness_level === "severe").length },
          ].map((stat) => (
            <div key={stat.label} className="ds-stat">
              <p className="ds-stat-value">{stat.value}</p>
              <p className="ds-stat-label">{stat.label}</p>
            </div>
          ))}
        </div>

        {(recommendations.notes || roadmap.study_plan_message) && (
          <p className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-4 text-sm text-foreground">
            {recommendations.notes || roadmap.study_plan_message}
          </p>
        )}

        {roadmap.domain_analysis && Object.keys(roadmap.domain_analysis).length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2 border-t border-border pt-4">
            {Object.entries(roadmap.domain_analysis).map(([domain, data]) => (
              <Badge key={domain} variant={data.accuracy_percentage >= 70 ? "success" : "warning"}>
                {domain.replace(/_/g, " ")} {data.accuracy_percentage}%
              </Badge>
            ))}
          </div>
        )}

        {roadmap.learning_gaps?.length > 0 && (
          <ul className="mt-4 space-y-2 border-t border-border pt-4 text-sm text-muted">
            {roadmap.learning_gaps.map((gap, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-primary">→</span>
                {gap}
              </li>
            ))}
          </ul>
        )}
      </Card>

      {chapters.map((chapter, index) => (
        <Card key={index} hoverable>
          <div
            className="cursor-pointer"
            onClick={() => setExpandedChapter(expandedChapter === index ? null : index)}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-foreground">{chapter.chapter_name}</h3>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge variant={weaknessBadge(chapter.weakness_level)} size="sm">
                    {chapter.weakness_level}
                  </Badge>
                  <span className="font-mono text-xs text-muted">{chapter.accuracy_percentage}%</span>
                </div>
              </div>
              <span className="text-muted">{expandedChapter === index ? "▼" : "▶"}</span>
            </div>

            {expandedChapter === index && (
              <div className="mt-5 space-y-5 border-t border-border pt-5 animate-fade-in">
                {chapter.roadmap_steps?.length > 0 && (
                  <div>
                    <p className="ds-mono-label mb-3">Next steps</p>
                    <div className="space-y-2">
                      {chapter.roadmap_steps.map((step, i) => (
                        <div key={i} className="flex gap-3 rounded-lg bg-surface-raised p-3">
                          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/15 font-mono text-xs text-primary">
                            {step.step_number}
                          </span>
                          <div>
                            <p className="text-sm text-foreground">{step.objective}</p>
                            <p className="font-mono text-[10px] text-muted">~{step.estimated_time_minutes || 20} min</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {chapter.resources?.length > 0 && (
                  <div>
                    <p className="ds-mono-label mb-3">Free tutorials</p>
                    <div className="grid gap-3 md:grid-cols-2">
                      {chapter.resources.map((resource, i) => (
                        <a
                          key={i}
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ds-resource-link"
                        >
                          <div className="mb-2 flex items-center justify-between gap-2">
                            <span className="ds-badge-primary">{resource.level || resource.type}</span>
                            <Badge variant="info" size="sm">{resource.type}</Badge>
                          </div>
                          <p className="font-semibold text-sm text-foreground">{resource.title}</p>
                          <p className="mt-1 text-xs text-muted">{resource.description}</p>
                          <p className="mt-2 text-xs font-semibold text-primary">Open →</p>
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

      {allResources.length > 0 && (
        <Card title="All resources">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {allResources.map((resource, i) => (
              <a key={i} href={resource.url} target="_blank" rel="noopener noreferrer" className="ds-resource-link">
                <span className="ds-badge-muted">{resource.provider_label || resource.provider}</span>
                <p className="mt-2 text-sm font-semibold text-foreground">{resource.title}</p>
                {resource.chapter && (
                  <p className="mt-1 font-mono text-[10px] text-muted">{resource.chapter}</p>
                )}
              </a>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default LearningRoadmap;
