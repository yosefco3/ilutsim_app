import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import { ToastProvider } from './components/Toast';
import LoginPage from './pages/LoginPage';
import SubmitPage from './pages/SubmitPage';
import SuccessPage from './pages/SuccessPage';
import GuardsPage from './pages/GuardsPage';
import AdminConstraintsPage from './pages/AdminConstraintsPage';
import WeeksPage from './pages/WeeksPage';
import SubmissionsPage from './pages/SubmissionsPage';
import SubmissionDetailPage from './pages/SubmissionDetailPage';
import SettingsPage from './pages/SettingsPage';
import ExportPage from './pages/ExportPage';
import ImportConstraintsPage from './pages/ImportConstraintsPage';
import ProfilesPage from './pages/builder/ProfilesPage';
import PositionsPage from './pages/builder/PositionsPage';
import './styles/admin.css';

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
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
          <Route path="/guards/:guardId/constraints" element={<ProtectedRoute><AdminConstraintsPage /></ProtectedRoute>} />
          <Route path="/weeks" element={<ProtectedRoute><WeeksPage /></ProtectedRoute>} />
          <Route path="/submissions/:weekId" element={<ProtectedRoute><SubmissionDetailPage /></ProtectedRoute>} />
          <Route path="/submissions" element={<ProtectedRoute><SubmissionsPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          <Route path="/export" element={<ProtectedRoute><ExportPage /></ProtectedRoute>} />
          <Route path="/import" element={<ProtectedRoute><ImportConstraintsPage /></ProtectedRoute>} />
          {/* Part B — Schedule Builder */}
          <Route path="/builder/profiles" element={<ProtectedRoute><ProfilesPage /></ProtectedRoute>} />
          <Route path="/builder/positions" element={<ProtectedRoute><PositionsPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/guards" replace />} />
        </Routes>
      </main>
    </>
  );
}
