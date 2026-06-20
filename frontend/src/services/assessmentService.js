import api from './api';

export const assessmentService = {
  // Start initial assessment
  startAssessment: async (studentId, subject) => {
    const response = await api.post('/assessment/start', { studentId, subject });
    return response.data;
  },
  
  // Submit answer and get next question
  submitAnswer: async (assessmentId, questionId, answer) => {
    const response = await api.post('/assessment/answer', {
      assessmentId,
      questionId,
      answer,
    });
    return response.data;
  },
  
  // Get assessment results
  getResults: async (assessmentId) => {
    const response = await api.get(`/assessment/${assessmentId}/results`);
    return response.data;
  },
};