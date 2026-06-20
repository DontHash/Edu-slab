import api from "./api";

const progressService = {
  /**
   * Get progress data for current student
   */
  async getMyProgress() {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user || !user.id) {
      throw new Error("User not authenticated");
    }

    const response = await api.get(`/progress/student/${user.id}`);
    return response.data;
  },

  /**
   * Get progress data for a specific student (teacher/admin only)
   */
  async getStudentProgress(studentId) {
    const response = await api.get(`/progress/student/${studentId}`);
    return response.data;
  },

  /**
   * Update student progress (teacher/admin only)
   */
  async updateStudentProgress(studentId, progressData) {
    const response = await api.put(
      `/progress/student/${studentId}`,
      progressData
    );
    return response.data;
  },
};

export default progressService;
