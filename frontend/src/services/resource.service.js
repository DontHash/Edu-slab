import api from "./api";

const resourceService = {
  /**
   * Get all resources with optional filters
   */
  async getResources(filters = {}) {
    const params = new URLSearchParams();

    if (filters.subject) params.append("subject", filters.subject);
    if (filters.difficulty) params.append("difficulty", filters.difficulty);
    if (filters.type) params.append("resource_type", filters.type);

    const response = await api.get(`/resources?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a specific resource by ID
   */
  async getResource(resourceId) {
    const response = await api.get(`/resources/${resourceId}`);
    return response.data;
  },

  /**
   * Get recommended resources for current student
   */
  async getRecommendedResources() {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user || !user.id) {
      throw new Error("User not authenticated");
    }

    const response = await api.get(`/resources/recommended/${user.id}`);
    return response.data;
  },

  /**
   * Get recommended resources for a specific student (teacher/admin only)
   */
  async getStudentRecommendedResources(studentId) {
    const response = await api.get(`/resources/recommended/${studentId}`);
    return response.data;
  },

  /**
   * Create a new resource (teacher/admin only)
   */
  async createResource(resourceData) {
    const response = await api.post("/v1/resources", resourceData);
    return response.data;
  },
};

export default resourceService;
