import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Alert from "../../components/common/Alert";
import Button from "../../components/common/Button";
import Input from "../../components/common/Input";
import useAuthStore from "../../store/authStore";

const Login = () => {
  const navigate = useNavigate();
  const { login, loading, error: authError, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    clearError();

    try {
      await login(formData);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Invalid credentials. Please try again.");
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4 sm:p-6"
      style={{ backgroundColor: "#DDD0C8" }}
    >
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 shadow-2xl"
            style={{ backgroundColor: "#323232", border: "2px solid #C9BDB3" }}
          >
            <svg
              className="w-9 h-9"
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
          <h1 className="text-4xl font-bold mb-2" style={{ color: "#323232" }}>
            EduAssess
          </h1>
          <p className="font-medium" style={{ color: "#5A5A5A" }}>
            Peer-to-Peer Learning Platform
          </p>
        </div>

        <div
          className="rounded-2xl shadow-2xl p-8"
          style={{ backgroundColor: "#F5EDE5", border: "1px solid #C9BDB3" }}
        >
          <h2 className="text-2xl font-bold mb-6" style={{ color: "#323232" }}>
            Welcome back
          </h2>

          {error && (
            <Alert type="error" message={error} onClose={() => setError("")} />
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="Enter your email"
              required
            />

            <Input
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              placeholder="Enter your password"
              required
            />

            <Button type="submit" fullWidth loading={loading}>
              Login
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Register here
            </Link>
          </div>

          <div className="mt-4 text-center">
            <Link
              to="/forgot-password"
              className="text-sm text-gray-600 hover:text-gray-700"
            >
              Forgot password?
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
