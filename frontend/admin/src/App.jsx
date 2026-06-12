import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import SubmitPage from './pages/SubmitPage';
import SuccessPage from './pages/SuccessPage';
import GuardsPage from './pages/GuardsPage';
import WeeksPage from './pages/WeeksPage';
import EventsPage from './pages/EventsPage';
import SubmissionsPage from './pages/SubmissionsPage';
import SubmissionDetailPage from './pages/SubmissionDetailPage';
import SettingsPage from './pages/SettingsPage';
import ExportPage from './pages/ExportPage';
import './styles/admin.css';

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

function AppContent() {
  const location = useLocation();
  const hideNavbar = location.pathname === '/submit' || location.pathname === '/submit/success';

  return (
    <>
      {!hideNavbar && <Navbar />}
      <main className="main-content">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/submit" element={<SubmitPage />} />
          <Route path="/submit/success" element={<SuccessPage />} />
          <Route path="/guards" element={<ProtectedRoute><GuardsPage /></ProtectedRoute>} />
          <Route path="/weeks" element={<ProtectedRoute><WeeksPage /></ProtectedRoute>} />
          <Route path="/events" element={<ProtectedRoute><EventsPage /></ProtectedRoute>} />
          <Route path="/submissions/:weekId" element={<ProtectedRoute><SubmissionDetailPage /></ProtectedRoute>} />
          <Route path="/submissions" element={<ProtectedRoute><SubmissionsPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          <Route path="/export" element={<ProtectedRoute><ExportPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/guards" replace />} />
        </Routes>
      </main>
    </>
  );
}
