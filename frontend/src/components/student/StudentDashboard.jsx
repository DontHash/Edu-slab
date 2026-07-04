import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ragQuestionService from "../../services/ragQuestion.service";
import useAuthStore from "../../store/authStore";
import Card from "../common/Card";
import { SKILL_AREAS, SKILL_LABELS } from "../../constants/skills";

const StudentDashboard = () => {
  const { refreshUser } = useAuthStore();
  const [recentActivities, setRecentActivities] = useState([]);
  const [areasForImprovement, setAreasForImprovement] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        await refreshUser();

        const activitiesData = await ragQuestionService.getRecentActivities(5);
        setRecentActivities(activitiesData.activities || []);

        const progressData = await ragQuestionService.getAllSubjectsProgress();
        const allWeaknesses = [];

        Object.entries(progressData.subjects_progress || {}).forEach(
          ([subject, data]) => {
            if (!data.has_data) return;

            (data.critical_weaknesses || []).forEach((weakness) => {
              allWeaknesses.push({
                subject: subject.charAt(0).toUpperCase() + subject.slice(1),
                chapter: weakness.chapter,
                accuracy: weakness.accuracy,
                severity: "critical",
              });
            });

            (data.areas_to_improve || []).slice(0, 2).forEach((area) => {
              allWeaknesses.push({
                subject: subject.charAt(0).toUpperCase() + subject.slice(1),
                chapter: area.chapter,
                accuracy: area.accuracy,
                severity: "moderate",
              });
            });
          }
        );

        allWeaknesses.sort((a, b) => a.accuracy - b.accuracy);
        setAreasForImprovement(allWeaknesses.slice(0, 6));
      } catch (err) {
        console.error("Dashboard load failed:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [refreshUser]);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <header className="ds-page-header">
        <p className="ds-mono-label mb-2 text-primary">Diagnostic platform</p>
        <h1 className="ds-page-title">Your learning cockpit</h1>
        <p className="ds-page-subtitle">
          Assess skills, track weak topics, and follow a curated study roadmap.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {SKILL_AREAS.map((area, i) => (
          <div
            key={area}
            className={`ds-stat animate-slide-up stagger-${i + 1}`}
          >
            <p className="ds-stat-value">{SKILL_LABELS[area].split(" ")[0]}</p>
            <p className="ds-stat-label">{SKILL_LABELS[area]}</p>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <Link to="/assessment" className="ds-btn-primary">
          Start assessment
        </Link>
        <Link to="/resources" className="ds-btn-outline">
          Learning roadmap
        </Link>
        <Link to="/my-progress" className="ds-btn-outline">
          My progress
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Areas for improvement">
          {areasForImprovement.length === 0 ? (
            <p className="text-sm text-muted">
              No weaknesses recorded yet. Take an assessment to get started.
            </p>
          ) : (
            <ul className="space-y-3">
              {areasForImprovement.map((item, idx) => (
                <li
                  key={idx}
                  className="flex items-center justify-between border-b border-border pb-3 last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {item.chapter}
                    </p>
                    <p className="ds-mono-label mt-0.5">{item.subject}</p>
                  </div>
                  <span
                    className={`font-mono text-sm ${
                      item.severity === "critical" ? "text-danger" : "text-warning"
                    }`}
                  >
                    {item.accuracy}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Recent activity">
          {recentActivities.length === 0 ? (
            <p className="text-sm text-muted">No recent activity.</p>
          ) : (
            <ul className="space-y-3">
              {recentActivities.map((activity, idx) => (
                <li
                  key={idx}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-foreground capitalize">
                    {activity.subject} · {activity.chapter || "Diagnostic"}
                  </span>
                  {activity.score != null && (
                    <span className="font-mono text-primary">{activity.score}</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
};

export default StudentDashboard;
