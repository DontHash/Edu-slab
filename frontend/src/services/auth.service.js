import api from "./api";

class AuthService {
  async login(credentials) {
    const response = await api.post("/auth/login", credentials);
    if (response.data.token) {
      localStorage.setItem("authToken", response.data.token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  }

  async register(userData) {
    const response = await api.post("/auth/register", {
      email: userData.email,
      name: userData.name,
      password: userData.password,
      role: "student",
      school_id: null,
      current_level: userData.gradeLevel ? parseInt(userData.gradeLevel) : null,
    });
    return response.data;
  }

  logout() {
    localStorage.removeItem("authToken");
    localStorage.removeItem("user");
    return true;
  }

  getCurrentUser() {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated() {
    return !!localStorage.getItem("authToken");
  }

  getToken() {
    return localStorage.getItem("authToken");
  }

  async getMe() {
    const response = await api.get("/auth/me");
    if (response.data) {
      localStorage.setItem("user", JSON.stringify(response.data));
    }
    return response.data;
  }

  async updateProfile(userData) {
    const response = await api.patch("/auth/profile", userData);
    if (response.data) {
      localStorage.setItem("user", JSON.stringify(response.data));
    }
    return response.data;
  }
}

export default new AuthService();
