import DashboardLayout from "../../components/layout/DashboardLayout";
import SubjectProgressChart from "../../components/student/SubjectProgressChart";
import useAuthStore from "../../store/authStore";

const MyProgressPage = () => {
  const { user } = useAuthStore();

  return (
    <DashboardLayout user={user}>
      <div>
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2" style={{ color: "#323232" }}>
            My Progress
          </h1>
          <p className="text-base" style={{ color: "#5A5A5A" }}>
            Track your learning journey across all subjects with detailed
            analytics and chapter-wise breakdown
          </p>
        </div>

        <SubjectProgressChart />
      </div>
    </DashboardLayout>
  );
};

export default MyProgressPage;
