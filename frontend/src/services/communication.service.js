/**
 * Communication Service - Chat, Video Calls, and File Sharing
 */
import api from './api';

const communicationService = {
  // ===== CHAT =====
  
  /**
   * Send a chat message to matched peer
   */
  sendMessage: async (matchId, receiverId, message, messageType = 'text', fileData = null) => {
    const response = await api.post('/matching/chat/send', {
      match_id: matchId,
      receiver_id: receiverId,
      message,
      message_type: messageType,
      file_url: fileData?.file_url,
      file_name: fileData?.file_name,
      file_size: fileData?.file_size,
      file_type: fileData?.file_type,
    });
    return response.data;
  },

  /**
   * Get chat history for a match
   */
  getChatHistory: async (matchId) => {
    const response = await api.get(`/matching/chat/${matchId}`);
    return response.data;
  },

  /**
   * Mark message as read
   */
  markMessageRead: async (messageId) => {
    const response = await api.patch(`/matching/chat/${messageId}/read`);
    return response.data;
  },

  // ===== SESSIONS & VIDEO CALLS =====

  /**
   * Create a tutoring session (text, video_call, or in_person)
   */
  createSession: async (matchId, communicationMethod, scheduledAt = null, meetingLocation = null) => {
    const response = await api.post('/matching/session/create', {
      match_id: matchId,
      communication_method: communicationMethod,
      scheduled_at: scheduledAt,
      meeting_location: meetingLocation,
    });
    return response.data;
  },

  /**
   * Update session details
   */
  updateSession: async (sessionId, updateData) => {
    const response = await api.patch(`/matching/session/${sessionId}`, updateData);
    return response.data;
  },

  /**
   * Get all sessions for a match
   */
  getSessions: async (matchId) => {
    const response = await api.get(`/matching/session/${matchId}/list`);
    return response.data;
  },

  /**
   * Start a video call session (generates Google Meet link)
   */
  startVideoCall: async (matchId, scheduledAt = null) => {
    return await communicationService.createSession(matchId, 'video_call', scheduledAt);
  },

  /**
   * Schedule an in-person meeting
   */
  scheduleInPerson: async (matchId, location, scheduledAt) => {
    return await communicationService.createSession(matchId, 'in_person', scheduledAt, location);
  },

  // ===== FILE & RESOURCE SHARING =====

  /**
   * Share a resource with matched peer
   */
  shareResource: async (resourceData) => {
    const response = await api.post('/matching/resource/share', resourceData);
    return response.data;
  },

  /**
   * Get all shared resources for a match
   */
  getSharedResources: async (matchId) => {
    const response = await api.get(`/matching/resource/${matchId}/list`);
    return response.data;
  },

  /**
   * Share a file
   */
  shareFile: async (matchId, title, fileUrl, fileName, fileSize, fileType, description = null) => {
    return await communicationService.shareResource({
      match_id: matchId,
      title,
      description,
      resource_type: fileType.startsWith('image/') ? 'image' : 'pdf',
      file_url: fileUrl,
      file_name: fileName,
      file_size: fileSize,
    });
  },

  /**
   * Share a link
   */
  shareLink: async (matchId, title, url, description = null) => {
    return await communicationService.shareResource({
      match_id: matchId,
      title,
      description,
      resource_type: 'link',
      external_link: url,
    });
  },

  /**
   * Share a note
   */
  shareNote: async (matchId, title, content, subject = null, chapter = null) => {
    return await communicationService.shareResource({
      match_id: matchId,
      title,
      description: content,
      resource_type: 'note',
      subject,
      chapter,
    });
  },
};

export default communicationService;
