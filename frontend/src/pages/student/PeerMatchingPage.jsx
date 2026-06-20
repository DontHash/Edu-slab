import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import matchingService from '../../services/matching.service';

const PeerMatchingPage = () => {
  const [matches, setMatches] = useState({ tutoring_matches: [], learning_matches: [], total_matches: 0 });
  const [potentialMatches, setPotentialMatches] = useState({ can_help: [], need_help: [] });
  const [helpRequests, setHelpRequests] = useState([]);
  const [helpOffers, setHelpOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('learning'); // 'learning' or 'tutoring'

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    await Promise.all([
      fetchMatches(),
      fetchPotentialMatches(),
      fetchHelpRequests(),
      fetchHelpOffers(),
    ]);
  };

  const fetchMatches = async () => {
    try {
      setLoading(true);
      const data = await matchingService.getMyMatches();
      setMatches(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  const fetchPotentialMatches = async () => {
    try {
      const data = await matchingService.getPotentialMatches();
      setPotentialMatches(data);
    } catch (err) {
      console.error('Failed to load potential matches:', err);
    }
  };

  const fetchHelpRequests = async () => {
    try {
      const data = await matchingService.getAvailableHelpRequests();
      setHelpRequests(data);
    } catch (err) {
      console.error('Failed to load help requests:', err);
    }
  };

  const fetchHelpOffers = async () => {
    try {
      const data = await matchingService.getAvailableHelpOffers();
      setHelpOffers(data);
    } catch (err) {
      console.error('Failed to load help offers:', err);
    }
  };

  const handleOfferHelp = async (performanceId, message = null) => {
    try {
      await matchingService.createHelpOffer({ performance_id: performanceId, message });
      setSuccess('Help offer created! Other students can now connect with you.');
      await fetchHelpOffers();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create help offer');
    }
  };

  const handleRequestHelp = async (performanceId, message = null) => {
    try {
      await matchingService.createHelpRequest({ performance_id: performanceId, message });
      setSuccess('Help request created! Tutors will be notified.');
      await fetchHelpRequests();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create help request');
    }
  };

  const handleRespondToRequest = async (requestId) => {
    try {
      await matchingService.respondToHelpRequest(requestId);
      setSuccess('Response sent! The student will be notified.');
      await fetchHelpRequests();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to respond to request');
    }
  };

  const handleRespondToOffer = async (offerId) => {
    try {
      await matchingService.respondToHelpOffer(offerId);
      setSuccess('Response sent! The tutor will be notified.');
      await fetchHelpOffers();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to respond to offer');
    }
  };

  const handleStatusUpdate = async (matchId, status) => {
    try {
      await matchingService.updateMatchStatus(matchId, status);
      // Refresh matches
      await fetchMatches();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update match status');
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCompatibilityColor = (score) => {
    if (score >= 80) return 'text-green-600 font-semibold';
    if (score >= 60) return 'text-blue-600 font-semibold';
    if (score >= 40) return 'text-yellow-600 font-semibold';
    return 'text-red-600 font-semibold';
  };

  const MatchCard = ({ match, isLearning }) => (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-800">
              {isLearning ? match.tutor_name : match.learner_name}
            </h3>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeColor(match.status)}`}>
              {match.status}
            </span>
          </div>
          <p className="text-sm text-gray-600">{isLearning ? match.tutor_email : match.learner_email}</p>
          {(isLearning ? match.tutor_school : match.learner_school) && (
            <p className="text-sm text-gray-500 mt-1">
              🏫 {isLearning ? match.tutor_school : match.learner_school}
            </p>
          )}
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold mb-1">
            <span className={getCompatibilityColor(match.compatibility_score)}>
              {Math.round(match.compatibility_score)}%
            </span>
          </div>
          <p className="text-xs text-gray-500">Match Score</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">Subject</p>
          <p className="font-semibold text-blue-900">{match.subject}</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">Chapter</p>
          <p className="font-semibold text-purple-900">{match.chapter}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-green-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">
            {isLearning ? 'Tutor Score' : 'Your Score'}
          </p>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-green-700">
              {isLearning ? match.tutor_score : match.learner_score}
            </span>
            <span className="text-sm text-gray-600 ml-1">/10</span>
          </div>
        </div>
        <div className="bg-orange-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">
            {isLearning ? 'Your Score' : 'Learner Score'}
          </p>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold text-orange-700">
              {isLearning ? match.learner_score : match.tutor_score}
            </span>
            <span className="text-sm text-gray-600 ml-1">/10</span>
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-500 mb-4">
        Matched on: {new Date(match.matched_at).toLocaleDateString()}
        {match.accepted_at && (
          <> • Accepted: {new Date(match.accepted_at).toLocaleDateString()}</>
        )}
      </div>

      {match.status === 'pending' && (
        <div className="flex gap-2">
          <button
            onClick={() => handleStatusUpdate(match.id, 'accepted')}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
          >
            Accept Match
          </button>
          <button
            onClick={() => handleStatusUpdate(match.id, 'rejected')}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
          >
            Decline
          </button>
        </div>
      )}

      {match.status === 'accepted' && (
        <button
          onClick={() => handleStatusUpdate(match.id, 'completed')}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
        >
          Mark as Completed
        </button>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your matches...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Peer-to-Peer Learning</h1>
          <p className="text-gray-600">
            Connect with classmates for collaborative learning. High scorers teach, low scorers learn!
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {success}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Matches</p>
                <p className="text-2xl font-bold text-gray-900">{matches.total_matches}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Teaching</p>
                <p className="text-2xl font-bold text-gray-900">{matches.tutoring_matches.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Learning</p>
                <p className="text-2xl font-bold text-gray-900">{matches.learning_matches.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('learning')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'learning'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Learning From Others ({matches.learning_matches.length})
              </button>
              <button
                onClick={() => setActiveTab('tutoring')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'tutoring'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Teaching Others ({matches.tutoring_matches.length})
              </button>
            </nav>
          </div>
        </div>

        {/* Matches List */}
        <div>
          {activeTab === 'learning' && (
            <div>
              {matches.learning_matches.length === 0 ? (
                <div className="space-y-6">
                  {/* Main message */}
                  <div className="bg-white rounded-lg shadow p-8 text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Your Peer Tutors</h3>
                    <p className="text-gray-600 mb-4">Connect with students who excel in areas where you need help</p>
                    
                    {potentialMatches.need_help.length === 0 ? (
                      <p className="text-gray-500 text-sm">Complete your assessment to get matched with peers who can help!</p>
                    ) : null}
                  </div>

                  {/* Available Help Offers - Students offering to teach chapters you're weak in */}
                  {helpOffers.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="h-5 w-5 text-green-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Students Offering Help
                      </h4>
                      <div className="space-y-3">
                        {helpOffers.slice(0, 5).map((offer) => (
                          <div key={offer.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-gray-900">{offer.student_name}</span>
                                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                                    {offer.score}/10
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600">{offer.subject} • {offer.chapter}</p>
                                {offer.message && (
                                  <p className="text-sm text-gray-500 mt-2 italic">"{offer.message}"</p>
                                )}
                              </div>
                              <button
                                onClick={() => handleRespondToOffer(offer.id)}
                                className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition"
                              >
                                Connect
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Potential Matches - Chapters where you need help */}
                  {potentialMatches.need_help.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="h-5 w-5 text-orange-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Chapters Where You Need Help
                      </h4>
                      <div className="space-y-3">
                        {potentialMatches.need_help.map((perf) => (
                          <div key={perf.id} className="border border-orange-200 bg-orange-50 rounded-lg p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-gray-900">{perf.chapter}</span>
                                  <span className="px-2 py-1 bg-orange-200 text-orange-900 text-xs rounded-full font-medium">
                                    {perf.score}/10
                                  </span>
                                  <span className="text-xs text-gray-500">{perf.subject}</span>
                                </div>
                                <p className="text-sm text-gray-600">
                                  Weakness: {perf.weakness_level} • Accuracy: {perf.accuracy_percentage}%
                                </p>
                              </div>
                              <button
                                onClick={() => handleRequestHelp(perf.id)}
                                className="ml-4 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-lg transition whitespace-nowrap"
                              >
                                Request Help
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                matches.learning_matches.map((match) => (
                  <MatchCard key={match.id} match={match} isLearning={true} />
                ))
              )}
            </div>
          )}

          {activeTab === 'tutoring' && (
            <div>
              {matches.tutoring_matches.length === 0 ? (
                <div className="space-y-6">
                  {/* Main message */}
                  <div className="bg-white rounded-lg shadow p-8 text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Share Your Knowledge</h3>
                    <p className="text-gray-600 mb-4">Help peers learn from your strengths</p>
                    
                    {potentialMatches.can_help.length === 0 ? (
                      <p className="text-gray-500 text-sm">Score high on assessments to get matched with students who need your help!</p>
                    ) : null}
                  </div>

                  {/* Help Requests - Students asking for help in chapters you're strong in */}
                  {helpRequests.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="h-5 w-5 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        Students Requesting Help
                      </h4>
                      <div className="space-y-3">
                        {helpRequests.slice(0, 5).map((request) => (
                          <div key={request.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-gray-900">{request.student_name}</span>
                                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full font-medium">
                                    {request.score}/10
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600">{request.subject} • {request.chapter}</p>
                                {request.message && (
                                  <p className="text-sm text-gray-500 mt-2 italic">"{request.message}"</p>
                                )}
                              </div>
                              <button
                                onClick={() => handleRespondToRequest(request.id)}
                                className="ml-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition"
                              >
                                Offer Help
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Potential Matches - Chapters where you can help */}
                  {potentialMatches.can_help.length > 0 && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="h-5 w-5 text-green-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Chapters Where You Can Teach
                      </h4>
                      <div className="space-y-3">
                        {potentialMatches.can_help.map((perf) => (
                          <div key={perf.id} className="border border-green-200 bg-green-50 rounded-lg p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-gray-900">{perf.chapter}</span>
                                  <span className="px-2 py-1 bg-green-200 text-green-900 text-xs rounded-full font-medium">
                                    {perf.score}/10
                                  </span>
                                  <span className="text-xs text-gray-500">{perf.subject}</span>
                                </div>
                                <p className="text-sm text-gray-600">
                                  Accuracy: {perf.accuracy_percentage}% • Great understanding!
                                </p>
                              </div>
                              <button
                                onClick={() => handleOfferHelp(perf.id)}
                                className="ml-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition whitespace-nowrap"
                              >
                                Offer Help
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                matches.tutoring_matches.map((match) => (
                  <MatchCard key={match.id} match={match} isLearning={false} />
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PeerMatchingPage;
