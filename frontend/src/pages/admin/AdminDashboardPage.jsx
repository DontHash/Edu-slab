import React from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import AdminDashboard from "../../components/admin/AdminDashboard";

const AdminDashboardPage = () => {
  // Mock data
  const adminData = {
    totalSchools: 15,
    totalStudents: 1250,
    totalTeachers: 87,
    activeAssessments: 42,
    recentActivity: [
      {
        icon: "🏫",
        action: "New school registered",
        user: "Lincoln High School",
        time: "2 hours ago",
      },
      {
        icon: "👥",
        action: "New teacher added",
        user: "John Smith",
        time: "5 hours ago",
      },
    ],
    alerts: [
      {
        type: "warning",
        title: "Server Maintenance",
        message: "Scheduled maintenance on Dec 25",
        time: "1 hour ago",
      },
    ],
  };

  const user = { name: "Admin", role: "admin" };

  return (
    <DashboardLayout user={user}>
      <AdminDashboard admin={adminData} />
    </DashboardLayout>
  );
};

export default AdminDashboardPage;
