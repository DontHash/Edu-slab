import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import DashboardLayout from "../../components/layout/DashboardLayout";
import LearningRoadmap from "../../components/student/LearningRoadmap";
import resourceService from "../../services/resource.service";
import useAuthStore from "../../store/authStore";

const ResourcesPage = () => {
  const { user } = useAuthStore();
  const [searchParams] = useSearchParams();
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get subject from URL params
  const subjectParam = searchParams.get("subject");

  const [selectedSubject, setSelectedSubject] = useState(
    subjectParam || "Maths"
  );

  const subjects = ["Maths", "English", "Science"];

  // Update when URL params change
  useEffect(() => {
    if (subjectParam) setSelectedSubject(subjectParam);
  }, [subjectParam]);

  useEffect(() => {
    const fetchResources = async () => {
      try {
        setLoading(true);
        // First try to get recommended resources based on student's progress
        try {
          const recommendedResources =
            await resourceService.getRecommendedResources();
          if (recommendedResources && recommendedResources.length > 0) {
            setResources(recommendedResources);
            return;
          }
        } catch (err) {
          console.log("No recommended resources, fetching all resources");
        }

        // If no recommended resources, get all resources
        const allResources = await resourceService.getResources();
        setResources(allResources);
      } catch (err) {
        console.error("Error fetching resources:", err);
        setError(err.message || "Failed to load resources");
      } finally {
        setLoading(false);
      }
    };

    fetchResources();
  }, []);

  return (
    <DashboardLayout user={user}>
      <div>
        <h1 className="text-3xl font-bold mb-6" style={{ color: "#323232" }}>
          Learning Resources
        </h1>

        {/* Subject Filter */}
        <div className="flex gap-2 mb-6">
          {subjects.map((subject) => (
            <button
              key={subject}
              onClick={() => setSelectedSubject(subject)}
              className={`px-5 py-2.5 rounded-lg font-medium transition-all shadow-sm`}
              style={
                selectedSubject === subject
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
              {subject}
            </button>
          ))}
        </div>

        {/* Content */}
        <LearningRoadmap subject={selectedSubject} />
      </div>
    </DashboardLayout>
  );
};

export default ResourcesPage;
