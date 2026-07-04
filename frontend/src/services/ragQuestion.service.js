/**
 * Assessment question service — Nepal CDC curriculum bank (local, no cloud API)
 */
import api from "./api";

const ragQuestionService = {
  async generateQuestions(chapter, subject = null, numQuestions = 1, grade = null) {
    const response = await api.post("/rag/generate-questions", {
      chapter,
      subject,
      num_questions: numQuestions,
      grade,
    });
    return response.data;
  },

  async getCurriculum(grade = null) {
    const response = await api.get("/rag/curriculum", {
      params: grade ? { grade } : {},
    });
    return response.data;
  },

  async getAvailableChapters(subject = null, grade = null) {
    const response = await api.get("/rag/available-chapters", {
      params: { subject, grade },
    });
    return response.data;
  },

  async startAdaptiveSession(subject, grade = null) {
    const response = await api.post("/rag/adaptive/start", {
      subject,
      grade,
    });
    return response.data;
  },

  async submitAdaptiveAnswer(sessionId, questionId, answer) {
    const response = await api.post(`/rag/adaptive/${sessionId}/answer`, {
      question_id: questionId,
      answer,
    });
    return response.data;
  },

  async finishAdaptiveSession(sessionId) {
    const response = await api.post(`/rag/adaptive/${sessionId}/finish`);
    return response.data;
  },

  async submitAssessment(chapter, subject, answers) {
    const response = await api.post("/rag/submit-assessment", {
      chapter,
      subject,
      answers,
    });
    return response.data;
  },

  async getUserAssessments() {
    const response = await api.get("/rag/user-assessments");
    return response.data;
  },

  async getAssessmentDetails(assessmentId) {
    const response = await api.get(`/rag/assessment/${assessmentId}`);
    return response.data;
  },

  async getEvaluationStatus() {
    const response = await api.get("/rag/evaluation-status");
    return response.data;
  },

  async getEvaluation(assessmentId) {
    const response = await api.get(`/rag/evaluate-assessment/${assessmentId}`);
    return response.data;
  },

  async getRecentActivities(limit = 10) {
    const response = await api.get("/rag/recent-activities", {
      params: { limit },
    });
    return response.data;
  },

  async getSubjectProgress(subject) {
    const response = await api.get(`/rag/subject-progress/${subject}`);
    return response.data;
  },

  async getLearningRoadmap(subject) {
    const response = await api.get(`/rag/learning-roadmap/${subject}`);
    return response.data;
  },

  async getAllSubjectsProgress() {
    const response = await api.get("/rag/all-subjects-progress");
    return response.data;
  },
};

export default ragQuestionService;
