import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, requireAdminOrHR = false }) {
  const { user, isAdminOrHR } = useAuth();

  if (!user) return <Navigate to="/login" replace />;
  if (requireAdminOrHR && !isAdminOrHR) return <Navigate to="/dashboard" replace />;

  return children;
}
