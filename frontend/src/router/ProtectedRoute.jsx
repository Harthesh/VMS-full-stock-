import { Navigate, useLocation } from "react-router-dom";
import LoadingSpinner from "../components/common/LoadingSpinner";
import useAuth from "../hooks/useAuth";

export default function ProtectedRoute({ children, roles = [] }) {
  const location = useLocation();
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div className="mx-auto mt-24 max-w-md">
        <LoadingSpinner label="Restoring your session..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const roleKeys = user?.roles?.map((role) => role.key) || [];
  if (roles.length && !roleKeys.includes("admin") && !roles.some((role) => roleKeys.includes(role))) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

