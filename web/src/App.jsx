import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Entry from './pages/Entry';
import Cases from './pages/Cases';
import CaseDetail from './pages/CaseDetail';
import Tasks from './pages/Tasks';
import Sobo from './pages/Sobo';
import Directories from './pages/Directories';
import Templates from './pages/Templates';
import Settings from './pages/Settings';

const ReShell = lazy(() => import('./re/ReShell'));

// Helper component to redirect root path "/" to dashboard or sobo based on user role
function RootRedirect() {
  const { isGuest } = useAuth();
  if (isGuest) {
    return <Navigate to="/sobo" replace />;
  }
  return <Navigate to="/dashboard" replace />;
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected Monorepo Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <RootRedirect />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/entry"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Entry />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/cases"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Cases />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/cases/:id"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <CaseDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Tasks />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/sobo"
          element={
            <ProtectedRoute>
              <Layout>
                <Sobo />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/directories/:tab?"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Directories />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizations"
          element={
            <ProtectedRoute adminOnly={true}>
              <Navigate to="/directories/organizations" replace />
            </ProtectedRoute>
          }
        />
        <Route
          path="/delivery"
          element={
            <ProtectedRoute adminOnly={true}>
              <Navigate to="/directories/delivery" replace />
            </ProtectedRoute>
          }
        />
        <Route
          path="/templates"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Templates />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute adminOnly={true}>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Isolated CenValue RE / Astryx spike */}
        <Route
          path="/re"
          element={
            <ProtectedRoute adminOnly={true}>
              <Suspense fallback={<div>Đang tải CenValue RE...</div>}>
                <ReShell />
              </Suspense>
            </ProtectedRoute>
          }
        />

        {/* Catch-all Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
