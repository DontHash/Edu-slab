/**
 * Header Component
 *
 * TODO:
 * 1. Add user profile dropdown
 * 2. Add notifications icon
 * 3. Add navigation links based on user role
 * 4. Implement logout functionality
 * 5. Make responsive with mobile menu
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../../store/authStore";

const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header
      className="sticky top-0 z-50 backdrop-blur-md shadow-sm"
      style={{ backgroundColor: "#DDD0C8", borderBottom: "1px solid #C9BDB3" }}
    >
      <div className="container mx-auto px-4 sm:px-6 py-3.5">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center shadow-md"
              style={{ backgroundColor: "#323232" }}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="#DDD0C8"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h1 className="text-xl font-bold" style={{ color: "#323232" }}>
              Edu Assist
            </h1>
          </Link>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 transition-colors"
            style={{ color: "#5A5A5A" }}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {mobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-1">
            <Link
              to="/dashboard"
              className="px-4 py-2 rounded-lg transition-all font-medium text-sm"
              style={{ color: "#323232" }}
            >
              Dashboard
            </Link>
          </nav>

          {/* Desktop User Menu */}
          <div className="hidden md:flex items-center space-x-3">
            {user ? (
              <>
                <div
                  className="flex items-center space-x-2 px-3 py-2 rounded-lg"
                  style={{
                    backgroundColor: "#E8DDD3",
                    border: "1px solid #C9BDB3",
                  }}
                >
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold shadow-md"
                    style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
                  >
                    {user.name?.charAt(0).toUpperCase()}
                  </div>
                  <span
                    className="text-sm font-medium"
                    style={{ color: "#323232" }}
                  >
                    {user.name}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                  style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 rounded-md transition-colors text-sm"
                style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
              >
                Login
              </Link>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div
            className="md:hidden mt-4 pb-4 space-y-2 pt-4"
            style={{ borderTop: "1px solid #C9BDB3" }}
          >
            <Link
              to="/dashboard"
              className="block px-4 py-2 rounded-lg transition-colors"
              style={{ color: "#323232" }}
              onClick={() => setMobileMenuOpen(false)}
            >
              Dashboard
            </Link>
            {user ? (
              <button
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
                className="w-full text-left px-4 py-2 rounded-lg transition-colors"
                style={{ color: "#323232", backgroundColor: "#F5EDE5" }}
              >
                Logout
              </button>
            ) : (
              <Link
                to="/login"
                className="block px-4 py-2 rounded-lg transition-colors"
                style={{ color: "#323232", backgroundColor: "#F5EDE5" }}
                onClick={() => setMobileMenuOpen(false)}
              >
                Login
              </Link>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
