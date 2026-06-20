/**
 * Matching Service - API calls for peer-to-peer matching
 */
import api from "./api";

const matchingService = {
  /**
   * Update student chapter performance from evaluation files
   */
  updateStudentPerformance: async (userId) => {
    const response = await api.post(`/matching/update-performance/${userId}`);
    return response.data;
  },

  /**
   * Create peer-to-peer matches for a specific chapter
   */
  createMatches: async (matchingData) => {
    const response = await api.post("/matching/create-matches", matchingData);
    return response.data;
  },

  /**
   * Get all matches for the current student
   */
  getMyMatches: async () => {
    const response = await api.get("/matching/my-matches");
    return response.data;
  },

  /**
   * Update match status (accept, reject, complete)
   */
  updateMatchStatus: async (matchId, status) => {
    const response = await api.patch(`/matching/match/${matchId}/status`, {
      status,
    });
    return response.data;
  },

  /**
   * Get available chapters for matching
   */
  getAvailableChapters: async (subject = null) => {
    const params = subject ? { subject } : {};
    const response = await api.get("/matching/available-chapters", { params });
    return response.data;
  },

  /**
   * Get matching statistics
   */
  getMatchingStats: async (subject = null, chapter = null) => {
    const params = {};
    if (subject) params.subject = subject;
    if (chapter) params.chapter = chapter;
    const response = await api.get("/matching/stats", { params });
    return response.data;
  },

  /**
   * Get student chapter performance
   */
  getStudentPerformance: async (studentId, subject = null) => {
    const params = subject ? { subject } : {};
    const response = await api.get(
      `/matching/student/${studentId}/performance`,
      { params }
    );
    return response.data;
  },

  /**
   * Get automatic potential match suggestions
   */
  getPotentialMatches: async (meetingType = "online") => {
    const response = await api.get("/matching/potential-matches", {
      params: { meeting_type: meetingType },
    });
    return response.data;
  },

  /**
   * Create a help request
   */
  createHelpRequest: async (data) => {
    const response = await api.post("/matching/help-request", data);
    return response.data;
  },

  /**
   * Create a help offer
   */
  createHelpOffer: async (data) => {
    const response = await api.post("/matching/help-offer", data);
    return response.data;
  },

  /**
   * Get available help requests
   */
  getAvailableHelpRequests: async () => {
    const response = await api.get("/matching/help-requests");
    return response.data;
  },

  /**
   * Get available help offers
   */
  getAvailableHelpOffers: async () => {
    const response = await api.get("/matching/help-offers");
    return response.data;
  },

  /**
   * Respond to a help request
   */
  respondToHelpRequest: async (requestId) => {
    const response = await api.post(
      `/matching/help-request/${requestId}/respond`
    );
    return response.data;
  },

  /**
   * Respond to a help offer
   */
  respondToHelpOffer: async (offerId) => {
    const response = await api.post(`/matching/help-offer/${offerId}/respond`);
    return response.data;
  },
};

export default matchingService;
