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
      <div className="p-6 text-charcoal-muted">Loading dashboard...</div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-charcoal">
          Diagnostic Dashboard
        </h1>
        <p className="text-charcoal-muted mt-1">
          Complete assessments across four skill areas, then review your topic
          reports and learning roadmap.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {SKILL_AREAS.map((area) => (
          <Card key={area} className="p-4">
            <p className="text-sm text-charcoal-muted">Skill area</p>
            <p className="font-semibold text-charcoal">{SKILL_LABELS[area]}</p>
          </Card>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          to="/assessment"
          className="px-4 py-2 rounded-lg text-cream bg-charcoal font-medium"
        >
          Start Assessment
        </Link>
        <Link
          to="/resources"
          className="px-4 py-2 rounded-lg font-medium border border-sand-border text-charcoal"
          style={{ backgroundColor: "#F5EDE5" }}
        >
          Learning Roadmap
        </Link>
        <Link
          to="/my-progress"
          className="px-4 py-2 rounded-lg font-medium border border-sand-border text-charcoal"
          style={{ backgroundColor: "#F5EDE5" }}
        >
          My Progress
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-5">
          <h2 className="text-lg font-semibold text-charcoal mb-4">
            Areas for Improvement
          </h2>
          {areasForImprovement.length === 0 ? (
            <p className="text-charcoal-muted text-sm">
              No weaknesses recorded yet. Take an assessment to get started.
            </p>
          ) : (
            <ul className="space-y-3">
              {areasForImprovement.map((item, idx) => (
                <li
                  key={idx}
                  className="flex justify-between items-center text-sm border-b border-sand-border pb-2"
                >
                  <span className="text-charcoal">
                    {item.subject} — {item.chapter}
                  </span>
                  <span className="text-charcoal-muted">{item.accuracy}%</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="p-5">
          <h2 className="text-lg font-semibold text-charcoal mb-4">
            Recent Activity
          </h2>
          {recentActivities.length === 0 ? (
            <p className="text-charcoal-muted text-sm">No recent activity.</p>
          ) : (
            <ul className="space-y-3">
              {recentActivities.map((activity, idx) => (
                <li key={idx} className="text-sm text-charcoal-muted">
                  {activity.message || activity.description || "Assessment activity"}
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
