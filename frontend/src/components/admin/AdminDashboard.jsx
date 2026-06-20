import React from "react";
import Card from "../common/Card";

const AdminDashboard = ({ admin }) => {
  const stats = [
    {
      label: "Total Schools",
      value: admin?.totalSchools || 0,
      icon: "🏫",
      color: "bg-blue-500",
    },
    {
      label: "Total Students",
      value: admin?.totalStudents || 0,
      icon: "👥",
      color: "bg-green-500",
    },
    {
      label: "Total Teachers",
      value: admin?.totalTeachers || 0,
      icon: "👨‍🏫",
      color: "bg-purple-500",
    },
    {
      label: "Active Assessments",
      value: admin?.activeAssessments || 0,
      icon: "📝",
      color: "bg-orange-500",
    },
  ];

  const recentActivity = admin?.recentActivity || [];
  const alerts = admin?.alerts || [];

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 sm:p-6 text-white">
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold mb-2">
          Admin Dashboard
        </h1>
        <p className="text-sm sm:text-base text-purple-100">
          Manage schools, users, and monitor system performance.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
        {stats.map((stat, index) => (
          <Card key={index}>
            <div className="flex items-center space-x-4">
              <div
                className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center text-2xl`}
              >
                {stat.icon}
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* System Alerts */}
      {alerts.length > 0 && (
        <Card title="System Alerts">
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  alert.type === "error"
                    ? "bg-red-50 border-red-500"
                    : alert.type === "warning"
                    ? "bg-yellow-50 border-yellow-500"
                    : "bg-blue-50 border-blue-500"
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-900">{alert.title}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {alert.message}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card title="Recent Activity">
          {recentActivity.length > 0 ? (
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 pb-4 border-b last:border-0"
                >
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-lg">
                    {activity.icon}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {activity.action}
                    </p>
                    <p className="text-sm text-gray-600">{activity.user}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          )}
        </Card>

        {/* Quick Stats */}
        <Card title="Performance Overview">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">System Uptime</span>
                <span className="font-semibold text-green-600">99.9%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: "99.9%" }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Average Test Completion</span>
                <span className="font-semibold text-blue-600">85%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: "85%" }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Student Engagement</span>
                <span className="font-semibold text-purple-600">78%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: "78%" }}
                ></div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors">
            <div className="text-3xl mb-2">🏫</div>
            <h4 className="font-medium text-gray-900">Add School</h4>
          </button>
          <button className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors">
            <div className="text-3xl mb-2">👥</div>
            <h4 className="font-medium text-gray-900">Manage Users</h4>
          </button>
          <button className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors">
            <div className="text-3xl mb-2">📊</div>
            <h4 className="font-medium text-gray-900">View Analytics</h4>
          </button>
          <button className="p-4 bg-orange-50 hover:bg-orange-100 rounded-lg text-center transition-colors">
            <div className="text-3xl mb-2">⚙️</div>
            <h4 className="font-medium text-gray-900">Settings</h4>
          </button>
        </div>
      </Card>
    </div>
  );
};

export default AdminDashboard;
