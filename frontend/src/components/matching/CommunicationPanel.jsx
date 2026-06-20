import { useState } from 'react';
import communicationService from '../../services/communication.service';

const CommunicationPanel = ({ match, currentUserId }) => {
  const [activeTab, setActiveTab] = useState('chat'); // chat, sessions, resources
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sessions, setSessions] = useState([]);
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(false);

  const otherUser = currentUserId === match.tutor_id 
    ? { id: match.learner_id, name: match.learner_name }
    : { id: match.tutor_id, name: match.tutor_name };

  // Load data when tab changes
  const loadTabData = async (tab) => {
    setLoading(true);
    try {
      if (tab === 'chat') {
        const chatHistory = await communicationService.getChatHistory(match.id);
        setMessages(chatHistory);
      } else if (tab === 'sessions') {
        const sessionsList = await communicationService.getSessions(match.id);
        setSessions(sessionsList);
      } else if (tab === 'resources') {
        const resourcesList = await communicationService.getSharedResources(match.id);
        setResources(resourcesList);
      }
    } catch (error) {
      console.error(`Failed to load ${tab}:`, error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    loadTabData(tab);
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    
    try {
      await communicationService.sendMessage(match.id, otherUser.id, newMessage);
      setNewMessage('');
      loadTabData('chat');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleStartVideoCall = async () => {
    try {
      const session = await communicationService.startVideoCall(match.id);
      window.open(session.meeting_link, '_blank');
      loadTabData('sessions');
    } catch (error) {
      console.error('Failed to start video call:', error);
    }
  };

  const handleShareResource = async (type) => {
    // This would open a modal for resource sharing
    console.log('Share resource:', type);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">
          Communication with {otherUser.name}
        </h3>
        <div className="flex gap-2">
          <span className="text-sm text-gray-500">
            {match.subject} - {match.chapter}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 mb-4">
        <button
          onClick={() => handleTabChange('chat')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'chat'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          💬 Chat
        </button>
        <button
          onClick={() => handleTabChange('sessions')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'sessions'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          📹 Sessions
        </button>
        <button
          onClick={() => handleTabChange('resources')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'resources'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          📁 Resources
        </button>
      </div>

      {/* Chat Tab */}
      {activeTab === 'chat' && (
        <div className="space-y-4">
          <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 space-y-3">
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : messages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No messages yet. Start the conversation!
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.sender_id === currentUserId ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-xs rounded-lg px-4 py-2 ${
                      msg.sender_id === currentUserId
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{msg.message}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSendMessage}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Sessions Tab */}
      {activeTab === 'sessions' && (
        <div className="space-y-4">
          <div className="flex gap-2 mb-4">
            <button
              onClick={handleStartVideoCall}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2"
            >
              📹 Start Video Call (Google Meet)
            </button>
            <button
              onClick={() => handleShareResource('in_person')}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 flex items-center gap-2"
            >
              📍 Schedule In-Person Meeting
            </button>
          </div>

          <div className="space-y-2">
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No sessions yet. Start a video call or schedule a meeting!
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium capitalize">
                        {session.communication_method.replace('_', ' ')}
                      </p>
                      {session.scheduled_at && (
                        <p className="text-sm text-gray-500">
                          {new Date(session.scheduled_at).toLocaleString()}
                        </p>
                      )}
                      {session.duration_minutes && (
                        <p className="text-sm text-gray-500">
                          Duration: {session.duration_minutes} minutes
                        </p>
                      )}
                    </div>
                    {session.meeting_link && (
                      <a
                        href={session.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                      >
                        Join Meeting
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Resources Tab */}
      {activeTab === 'resources' && (
        <div className="space-y-4">
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => handleShareResource('file')}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              📎 Share File
            </button>
            <button
              onClick={() => handleShareResource('link')}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              🔗 Share Link
            </button>
            <button
              onClick={() => handleShareResource('note')}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
            >
              📝 Share Note
            </button>
          </div>

          <div className="space-y-2">
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : resources.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No resources shared yet. Share files, links, or notes!
              </div>
            ) : (
              resources.map((resource) => (
                <div
                  key={resource.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium">{resource.title}</p>
                      {resource.description && (
                        <p className="text-sm text-gray-600 mt-1">
                          {resource.description}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        Shared by {resource.uploader_name} •{' '}
                        {new Date(resource.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {resource.file_url && (
                        <a
                          href={resource.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:text-blue-600"
                        >
                          Download
                        </a>
                      )}
                      {resource.external_link && (
                        <a
                          href={resource.external_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:text-blue-600"
                        >
                          Open Link
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CommunicationPanel;
