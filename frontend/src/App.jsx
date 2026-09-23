import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import AppShell from './components/layout/AppShell'
import ProtectedRoute from './components/ProtectedRoute'
import AcceptInvitationPage from './pages/AcceptInvitationPage'
import CreateOrgPage from './pages/CreateOrgPage'
import DashboardPage from './pages/DashboardPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import LoginPage from './pages/LoginPage'
import NewProjectPage from './pages/NewProjectPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import ProjectListPage from './pages/ProjectListPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import SettingsMembersPage from './pages/SettingsMembersPage'
import SignupPage from './pages/SignupPage'
import VerifyEmailPage from './pages/VerifyEmailPage'

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/signup', element: <SignupPage /> },
  { path: '/verify-email', element: <VerifyEmailPage /> },
  { path: '/forgot-password', element: <ForgotPasswordPage /> },
  { path: '/reset-password', element: <ResetPasswordPage /> },
  { path: '/accept-invitation', element: <AcceptInvitationPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      { path: '/create-organization', element: <CreateOrgPage /> },
      {
        element: <AppShell />,
        children: [
          { path: '/', element: <DashboardPage /> },
          { path: '/settings/members', element: <SettingsMembersPage /> },
          { path: '/projects', element: <ProjectListPage /> },
          { path: '/projects/new', element: <NewProjectPage /> },
          { path: '/projects/:projectId', element: <ProjectDetailPage /> },
        ],
      },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
