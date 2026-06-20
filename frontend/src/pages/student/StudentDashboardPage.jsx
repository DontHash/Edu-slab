import DashboardLayout from "../../components/layout/DashboardLayout";
import StudentDashboard from "../../components/student/StudentDashboard";
import useAuthStore from "../../store/authStore";

const StudentDashboardPage = () => {
  const { user } = useAuthStore();

  return (
    <DashboardLayout user={user}>
      <StudentDashboard />
    </DashboardLayout>
  );
};

export default StudentDashboardPage;
