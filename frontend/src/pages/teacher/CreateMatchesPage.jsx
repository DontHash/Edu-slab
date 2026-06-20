import { useState, useEffect } from 'react';
import matchingService from '../../services/matching.service';

const CreateMatchesPage = () => {
  const [availableChapters, setAvailableChapters] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedChapter, setSelectedChapter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [createdMatches, setCreatedMatches] = useState([]);

  useEffect(() => {
    fetchAvailableChapters();
  }, []);

  useEffect(() => {
    if (selectedSubject && selectedChapter) {
      fetchStats();
    }
  }, [selectedSubject, selectedChapter]);

  const fetchAvailableChapters = async () => {
    try {
      const data = await matchingService.getAvailableChapters();
      setAvailableChapters(data);
      if (data.length > 0) {
        setSelectedSubject(data[0].subject);
        if (data[0].chapters.length > 0) {
          setSelectedChapter(data[0].chapters[0]);
        }
      }
    } catch (err) {
      setError('Failed to load available chapters');
    }
  };

  const fetchStats = async () => {
    try {
      const data = await matchingService.getMatchingStats(selectedSubject, selectedChapter);
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleCreateMatches = async () => {
    if (!selectedSubject || !selectedChapter) {
      setError('Please select both subject and chapter');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const result = await matchingService.createMatches({
        subject: selectedSubject,
        chapter: selectedChapter,
      });

      setSuccess(`Successfully created ${result.matches_created} matches!`);
      setCreatedMatches(result.matches);
      await fetchStats(); // Refresh stats
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create matches');
    } finally {
      setLoading(false);
    }
  };

  const selectedSubjectData = availableChapters.find(s => s.subject === selectedSubject);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Peer-to-Peer Matches</h1>
          <p className="text-gray-600">
            Use the Asymmetric Gale-Shapley algorithm to match high-performing students with those who need help.
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Selection and Stats */}
          <div className="lg:col-span-1">
            {/* Selection Form */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Chapter</h2>

              <div className="space-y-4">
                {/* Subject Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <select
                    value={selectedSubject}
                    onChange={(e) => {
                      setSelectedSubject(e.target.value);
                      const subjectData = availableChapters.find(s => s.subject === e.target.value);
                      if (subjectData && subjectData.chapters.length > 0) {
                        setSelectedChapter(subjectData.chapters[0]);
                      }
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {availableChapters.map((subject) => (
                      <option key={subject.subject} value={subject.subject}>
                        {subject.subject} ({subject.total_students} students)
                      </option>
                    ))}
                  </select>
                </div>

                {/* Chapter Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chapter
                  </label>
                  <select
                    value={selectedChapter}
                    onChange={(e) => setSelectedChapter(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={!selectedSubjectData || selectedSubjectData.chapters.length === 0}
                  >
                    {selectedSubjectData?.chapters.map((chapter) => (
                      <option key={chapter} value={chapter}>
                        {chapter}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleCreateMatches}
                  disabled={loading || !selectedSubject || !selectedChapter}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Matches...
                    </>
                  ) : (
                    'Create Matches'
                  )}
                </button>
              </div>
            </div>

            {/* Statistics Card */}
            {stats && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Potential Tutors</p>
                      <p className="text-2xl font-bold text-green-700">{stats.total_potential_tutors}</p>
                      <p className="text-xs text-gray-500">Score ≥ 7/10</p>
                    </div>
                    <svg className="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Potential Learners</p>
                      <p className="text-2xl font-bold text-orange-700">{stats.total_potential_learners}</p>
                      <p className="text-xs text-gray-500">Score ≤ 5/10</p>
                    </div>
                    <svg className="h-10 w-10 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>

                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-2">Available Chapters</p>
                    <p className="text-lg font-bold text-blue-700">{stats.chapters_available.length}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Created Matches */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Recently Created Matches
                {createdMatches.length > 0 && (
                  <span className="ml-2 text-sm font-normal text-gray-600">
                    ({createdMatches.length} matches)
                  </span>
                )}
              </h2>

              {createdMatches.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  <p className="text-gray-500">No matches created yet. Select a chapter and click "Create Matches" to begin.</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-[600px] overflow-y-auto">
                  {createdMatches.map((match) => (
                    <div key={match.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm font-medium text-gray-700">Tutor:</span>
                            <span className="font-semibold text-gray-900">{match.tutor_name}</span>
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                              {match.tutor_score}/10
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-700">Learner:</span>
                            <span className="font-semibold text-gray-900">{match.learner_name}</span>
                            <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full font-medium">
                              {match.learner_score}/10
                            </span>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className="text-xl font-bold text-blue-600">
                            {Math.round(match.compatibility_score)}%
                          </div>
                          <p className="text-xs text-gray-500">Compatibility</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center">
                          <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                          </svg>
                          {match.chapter}
                        </span>
                        <span>•</span>
                        <span>{match.subject}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateMatchesPage;
