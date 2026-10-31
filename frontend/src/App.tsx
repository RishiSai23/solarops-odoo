import { Routes, Route, Navigate } from 'react-router-dom';
import DirectorDashboard from './pages/DirectorDashboard';
import ProjectsPage from './pages/ProjectsPage';
import SurveysPage from './pages/SurveysPage';
import InstallationsPage from './pages/InstallationsPage';
import PackagesPage from './pages/PackagesPage';
import ReportsPage from './pages/ReportsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/director" replace />} />
      <Route path="/director" element={<DirectorDashboard />} />
      <Route path="/director/projects" element={<ProjectsPage />} />
      <Route path="/director/surveys" element={<SurveysPage />} />
      <Route path="/director/installations" element={<InstallationsPage />} />
      <Route path="/director/packages" element={<PackagesPage />} />
      <Route path="/director/reports" element={<ReportsPage />} />
    </Routes>
  );
}
