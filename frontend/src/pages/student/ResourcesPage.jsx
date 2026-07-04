import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import DashboardLayout from "../../components/layout/DashboardLayout";
import LearningRoadmap from "../../components/student/LearningRoadmap";
import useAuthStore from "../../store/authStore";

const ResourcesPage = () => {
  const { user } = useAuthStore();
  const [searchParams] = useSearchParams();
  const subjectParam = searchParams.get("subject");
  const [selectedSubject, setSelectedSubject] = useState(subjectParam || "Maths");
  const subjects = ["Maths", "English", "Science"];

  useEffect(() => {
    if (subjectParam) setSelectedSubject(subjectParam);
  }, [subjectParam]);

  return (
    <DashboardLayout user={user}>
      <div className="animate-fade-in">
        <header className="ds-page-header">
          <p className="ds-mono-label mb-2 text-primary">Study plan</p>
          <h1 className="ds-page-title">Learning roadmap</h1>
          <p className="ds-page-subtitle">
            Free tutorials and next steps based on your latest diagnostic.
          </p>
        </header>

        <div className="mb-8 inline-flex rounded-xl border border-border bg-surface p-1">
          {subjects.map((subject) => (
            <button
              key={subject}
              onClick={() => setSelectedSubject(subject)}
              className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all duration-200 ${
                selectedSubject === subject
                  ? "bg-primary text-background shadow-glow-sm"
                  : "text-muted hover:text-foreground"
              }`}
            >
              {subject}
            </button>
          ))}
        </div>

        <LearningRoadmap subject={selectedSubject} />
      </div>
    </DashboardLayout>
  );
};

export default ResourcesPage;
