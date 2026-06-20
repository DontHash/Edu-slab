// Example: How to add Peer Matching routes to your React Router
// Add this to your main routing configuration file (e.g., App.jsx)

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import the new matching pages
import PeerMatchingPage from './pages/student/PeerMatchingPage';
import CreateMatchesPage from './pages/teacher/CreateMatchesPage';

// ... your other imports

function App() {
  return (
    <Router>
      <Routes>
        {/* ... your existing routes ... */}
        
        {/* Student Routes */}
        <Route path="/student/dashboard" element={<StudentDashboardPage />} />
        <Route path="/student/assessment" element={<RAGAssessmentPage />} />
        <Route path="/student/progress" element={<ProgressPage />} />
        
        {/* NEW: Peer Matching for Students */}
        <Route path="/student/peer-matching" element={<PeerMatchingPage />} />
        
        {/* Teacher Routes */}
        <Route path="/teacher/dashboard" element={<TeacherDashboardPage />} />
        <Route path="/teacher/students" element={<StudentsPage />} />
        
        {/* NEW: Create Matches for Teachers */}
        <Route path="/teacher/create-matches" element={<CreateMatchesPage />} />
        
        {/* Admin Routes */}
        <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
        
        {/* NEW: Create Matches for Admins */}
        <Route path="/admin/create-matches" element={<CreateMatchesPage />} />
        
        {/* ... your other routes ... */}
      </Routes>
    </Router>
  );
}

export default App;
