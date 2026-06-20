import apiService from "./api.service";

class AnalyticsService {
  async getOverallAnalytics() {
    return await apiService.get("/analytics/overall");
  }

  async getStudentAnalytics(studentId) {
    return await apiService.get(`/analytics/student/${studentId}`);
  }

  async getTeacherAnalytics(teacherId) {
    return await apiService.get(`/analytics/teacher/${teacherId}`);
  }

  async getSchoolAnalytics(schoolId) {
    return await apiService.get(`/analytics/school/${schoolId}`);
  }

  async getPerformanceByGrade() {
    return await apiService.get("/analytics/performance/grade");
  }

  async getPerformanceBySubject() {
    return await apiService.get("/analytics/performance/subject");
  }

  async getAttendanceData(filters = {}) {
    const params = new URLSearchParams(filters);
    return await apiService.get(`/analytics/attendance?${params}`);
  }

  async getWeeklyTrends() {
    return await apiService.get("/analytics/trends/weekly");
  }
}

export default new AnalyticsService();
