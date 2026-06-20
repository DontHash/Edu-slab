/**
 * RAG Question Service
 * Handles API calls for RAG-based question generation and assessment submission
 */
import api from "./api";

const ragQuestionService = {
  /**
   * Generate questions for a chapter using RAG
   */
  async generateQuestions(
    chapter,
    subject = null,
    numQuestions = 5,
    difficulty = "medium"
  ) {
    const response = await api.post("/rag/generate-questions", {
      chapter,
      subject,
      num_questions: numQuestions,
      difficulty,
    });
    return response.data;
  },

  /**
   * Get available chapters organized by subject
   */
  async getAvailableChapters(subject = null) {
    const response = await api.get("/rag/available-chapters", {
      params: { subject },
    });
    return response.data;
  },

  /**
   * Submit answers for an assessment
   */
  async submitAssessment(chapter, subject, answers) {
    const response = await api.post("/rag/submit-assessment", {
      chapter,
      subject,
      answers,
    });
    return response.data;
  },

  /**
   * Get all assessments for the current user
   */
  async getUserAssessments() {
    const response = await api.get("/rag/user-assessments");
    return response.data;
  },

  /**
   * Get details of a specific assessment
   */
  async getAssessmentDetails(assessmentId) {
    const response = await api.get(`/rag/assessment/${assessmentId}`);
    return response.data;
  },

  /**
   * Get evaluation results for an assessment
   */
  async getEvaluation(assessmentId) {
    const response = await api.get(`/rag/evaluate-assessment/${assessmentId}`);
    return response.data;
  },

  /**
   * Get recent activities (assessments taken)
   */
  async getRecentActivities(limit = 10) {
    const response = await api.get("/rag/recent-activities", {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get subject-specific progress analysis
   */
  async getSubjectProgress(subject) {
    const response = await api.get(`/rag/subject-progress/${subject}`);
    return response.data;
  },

  /**
   * Get progress for all subjects
   */
  async getAllSubjectsProgress() {
    const response = await api.get("/rag/all-subjects-progress");
    return response.data;
  },
};

export default ragQuestionService;
