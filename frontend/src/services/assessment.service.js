import apiService from "./api.service";

class AssessmentService {
  async getAssessments(filters = {}) {
    const params = new URLSearchParams(filters);
    return await apiService.get(`/assessments?${params}`);
  }

  async getAssessmentById(id) {
    return await apiService.get(`/assessments/${id}`);
  }

  async createAssessment(assessmentData) {
    return await apiService.post("/assessments", assessmentData);
  }

  async updateAssessment(id, assessmentData) {
    return await apiService.put(`/assessments/${id}`, assessmentData);
  }

  async deleteAssessment(id) {
    return await apiService.delete(`/assessments/${id}`);
  }

  async startAssessment(assessmentId) {
    return await apiService.post(`/assessments/${assessmentId}/start`);
  }

  async submitAnswer(assessmentId, questionId, answer) {
    return await apiService.post(`/assessments/${assessmentId}/answer`, {
      questionId,
      answer,
    });
  }

  async completeAssessment(assessmentId) {
    return await apiService.post(`/assessments/${assessmentId}/complete`);
  }

  async getAssessmentResults(assessmentId) {
    return await apiService.get(`/assessments/${assessmentId}/results`);
  }

  async getNextQuestion(assessmentId, currentLevel) {
    return await apiService.post(`/assessments/${assessmentId}/next-question`, {
      currentLevel,
    });
  }
}

export default new AssessmentService();
