
import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export default function ProtectedRoute() {
  const { user, loading } = useAuthStore();

  if (loading) {
    return (
      <div className="page-center">
        <div className="spinner" />
        <p>Checking your session...</p>
      </div>
    );
  }

  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
