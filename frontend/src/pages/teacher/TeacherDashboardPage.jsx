import DashboardLayout from "../../components/layout/DashboardLayout";
import TeacherDashboard from "../../components/teacher/TeacherDashboard";

const TeacherDashboardPage = () => {
  // Mock data
  const teacherData = {
    name: "Ms. Smith",
    teachingLevel: 9,
    canTeachGrades: "7-10",
    qualification: "Bachelor's in Mathematics",
    evaluationScore: 88,
    totalStudents: 45,
    activeAssessments: 8,
    avgPerformance: 78,
    pendingReviews: 12,
    teachingSubjects: [
      {
        name: "Mathematics",
        proficiency: 92,
        topics: ["Algebra", "Geometry", "Equations"],
        studentsCount: 25,
        assignedGrades: [8, 9],
      },
      {
        name: "English",
        proficiency: 78,
        topics: ["Grammar", "Essay Writing"],
        studentsCount: 20,
        assignedGrades: [8, 9],
      },
    ],
    assignedStudents: [
      {
        name: "John Doe",
        grade: 8,
        status: "active",
        weakAreas: ["Algebra", "Math: Fractions"],
        matchReason: "Needs help in Grade 8 Math topics",
      },
      {
        name: "Jane Smith",
        grade: 9,
        status: "active",
        weakAreas: ["English: Grammar", "Essay Writing"],
        matchReason: "Weak in Grade 9 English",
      },
      {
        name: "Mike Johnson",
        grade: 8,
        status: "needs attention",
        weakAreas: ["Math: Word Problems", "Equations"],
        matchReason: "Struggling with Grade 8 Math",
      },
      {
        name: "Sarah Williams",
        grade: 9,
        status: "active",
        weakAreas: ["Math: Geometry", "English: Reading Comp"],
        matchReason: "Multiple weak areas in Grade 9",
      },
    ],
    recentStudents: [
      {
        name: "John Doe",
        activity: "Completed Math Assessment",
        status: "completed",
      },
      {
        name: "Jane Smith",
        activity: "Started Science Test",
        status: "in-progress",
      },
    ],
    upcomingClasses: [
      { subject: "Mathematics", grade: "8", time: "10:00 AM", students: 25 },
      { subject: "Science", grade: "7", time: "2:00 PM", students: 20 },
    ],
  };

  const user = { name: "Ms. Smith", role: "teacher" };

  return (
    <DashboardLayout user={user}>
      <TeacherDashboard teacher={teacherData} />
    </DashboardLayout>
  );
};

export default TeacherDashboardPage;
