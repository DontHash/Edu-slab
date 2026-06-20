import { create } from "zustand";
import assessmentService from "../services/assessment.service";

const useAssessmentStore = create((set, get) => ({
  currentAssessment: null,
  currentQuestion: null,
  answers: {},
  loading: false,
  error: null,

  startAssessment: async (assessmentId) => {
    set({ loading: true, error: null });
    try {
      const assessment = await assessmentService.startAssessment(assessmentId);
      set({ currentAssessment: assessment, answers: {}, loading: false });
      return assessment;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  submitAnswer: async (questionId, answer) => {
    const { currentAssessment, answers } = get();
    set({ answers: { ...answers, [questionId]: answer } });

    try {
      await assessmentService.submitAnswer(
        currentAssessment.id,
        questionId,
        answer
      );
    } catch (error) {
      console.error("Error submitting answer:", error);
    }
  },

  getNextQuestion: async (currentLevel) => {
    const { currentAssessment } = get();
    set({ loading: true });
    try {
      const question = await assessmentService.getNextQuestion(
        currentAssessment.id,
        currentLevel
      );
      set({ currentQuestion: question, loading: false });
      return question;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  completeAssessment: async () => {
    const { currentAssessment } = get();
    set({ loading: true, error: null });
    try {
      const results = await assessmentService.completeAssessment(
        currentAssessment.id
      );
      set({ loading: false });
      return results;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  resetAssessment: () => {
    set({
      currentAssessment: null,
      currentQuestion: null,
      answers: {},
      error: null,
    });
  },
}));

export default useAssessmentStore;
