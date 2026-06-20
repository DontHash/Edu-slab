/**
 * Sidebar — diagnostic assessment platform navigation
 */

import { Link, useLocation } from "react-router-dom";
import useAuthStore from "../../store/authStore";

const Sidebar = () => {
  const { user } = useAuthStore();
  const location = useLocation();

  const menuItems = [
    {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
      label: "Dashboard",
      path: "/dashboard",
    },
    {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      label: "Assessment",
      path: "/assessment",
    },
    {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      label: "My Progress",
      path: "/my-progress",
    },
    {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      label: "Roadmap",
      path: "/resources",
    },
  ];

  return (
    <aside
      className="hidden lg:block w-64 h-screen sticky top-0 shadow-sm"
      style={{ backgroundColor: "#E8DDD3", borderRight: "1px solid #C9BDB3" }}
    >
      <div className="p-6">
        {/* User Profile Section */}
        <div
          className="mb-8 pb-6"
          style={{ borderBottom: "1px solid #C9BDB3" }}
        >
          <div
            className="w-14 h-14 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl font-bold shadow-lg"
            style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
          >
            {user?.name?.charAt(0).toUpperCase() || "U"}
          </div>
          <h3
            className="font-semibold text-center text-base"
            style={{ color: "#323232" }}
          >
            {user?.name || "Guest"}
          </h3>
          <p className="text-sm text-center mt-1" style={{ color: "#5A5A5A" }}>
            Student
          </p>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-1">
          {menuItems.map((item, index) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={index}
                to={item.path}
                className="flex items-center space-x-3 px-4 py-3 rounded-lg transition-all text-sm font-medium group"
                style={{
                  color: "#323232",
                  backgroundColor: isActive ? "#F5EDE5" : "transparent",
                  borderLeft: isActive
                    ? "3px solid #5A5A5A"
                    : "3px solid transparent",
                }}
              >
                <span
                  className="transition-colors"
                  style={{ color: isActive ? "#323232" : "#5A5A5A" }}
                >
                  {item.icon}
                </span>
                <span style={{ fontWeight: isActive ? "600" : "500" }}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
