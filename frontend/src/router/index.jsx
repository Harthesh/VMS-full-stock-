import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "../components/layout/AppLayout";
import ProtectedRoute from "./ProtectedRoute";
import ApprovalDetailPage from "../pages/ApprovalDetailPage";
import BadgePreviewPage from "../pages/BadgePreviewPage";
import BlacklistPage from "../pages/BlacklistPage";
import DashboardPage from "../pages/DashboardPage";
import ForgotPasswordPage from "../pages/ForgotPasswordPage";
import GateCheckInPage from "../pages/GateCheckInPage";
import GateCheckOutPage from "../pages/GateCheckOutPage";
import EmergencyPage from "../pages/EmergencyPage";
import GateScanPage from "../pages/GateScanPage";
import HospitalityPage from "../pages/HospitalityPage";
import InvitationsPage from "../pages/InvitationsPage";
import LoginPage from "../pages/LoginPage";
import PublicInvitationPage from "../pages/PublicInvitationPage";
import MyRequestsPage from "../pages/MyRequestsPage";
import NotFoundPage from "../pages/NotFoundPage";
import NotificationsPage from "../pages/NotificationsPage";
import PendingApprovalsPage from "../pages/PendingApprovalsPage";
import ReportsPage from "../pages/ReportsPage";
import AuditLogsPage from "../pages/AuditLogsPage";
import RequestCreatePage from "../pages/RequestCreatePage";
import RequestDetailPage from "../pages/RequestDetailPage";
import RequestEditPage from "../pages/RequestEditPage";
import RolesPage from "../pages/RolesPage";
import SettingsPage from "../pages/SettingsPage";
import UsersPage from "../pages/UsersPage";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/invite/:token" element={<PublicInvitationPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/requests" element={<MyRequestsPage />} />
                <Route path="/requests/new" element={<RequestCreatePage />} />
                <Route path="/requests/:id" element={<RequestDetailPage />} />
                <Route path="/requests/:id/edit" element={<RequestEditPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route
                  path="/approvals"
                  element={
                    <ProtectedRoute roles={["manager", "hod", "ceo_office", "security", "it", "bd_sales", "admin"]}>
                      <PendingApprovalsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/approvals/:id"
                  element={
                    <ProtectedRoute roles={["manager", "hod", "ceo_office", "security", "it", "bd_sales", "admin"]}>
                      <ApprovalDetailPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/gate/scan"
                  element={
                    <ProtectedRoute roles={["gatekeeper", "security", "admin"]}>
                      <GateScanPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/gate/check-in"
                  element={
                    <ProtectedRoute roles={["gatekeeper", "security", "admin"]}>
                      <GateCheckInPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/gate/check-out"
                  element={
                    <ProtectedRoute roles={["gatekeeper", "security", "admin"]}>
                      <GateCheckOutPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/invitations"
                  element={
                    <ProtectedRoute roles={["employee", "hr", "bd_sales", "manager", "hod", "admin"]}>
                      <InvitationsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/emergency"
                  element={
                    <ProtectedRoute roles={["security", "admin", "gatekeeper", "hr"]}>
                      <EmergencyPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/hospitality"
                  element={
                    <ProtectedRoute roles={["admin", "hr", "manager", "hod", "employee"]}>
                      <HospitalityPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/blacklist"
                  element={
                    <ProtectedRoute roles={["security", "gatekeeper", "admin"]}>
                      <BlacklistPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/users"
                  element={
                    <ProtectedRoute roles={["admin"]}>
                      <UsersPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/roles"
                  element={
                    <ProtectedRoute roles={["admin"]}>
                      <RolesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/audit-logs"
                  element={
                    <ProtectedRoute roles={["admin"]}>
                      <AuditLogsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute roles={["admin"]}>
                      <SettingsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/reports"
                  element={
                    <ProtectedRoute roles={["admin", "security", "hr", "bd_sales", "manager", "hod"]}>
                      <ReportsPage />
                    </ProtectedRoute>
                  }
                />
                <Route path="/badge/:id" element={<BadgePreviewPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </AppLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
