import api from "./api";

const ragQuestionService = {
  // ... existing methods ...

  async evaluateAssessment(assessmentId) {
    const response = await api.post(`/rag/evaluate-assessment/${assessmentId}`);
    return response.data;
  },

  async getAssessmentEvaluation(assessmentId) {
    try {
      const response = await api.get(
        `/rag/evaluate-assessment/${assessmentId}`
      );
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // No evaluation yet
      }
      throw error;
    }
  },
};

export default ragQuestionService;
