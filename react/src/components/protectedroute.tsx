import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requireAdmin = false }) => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (!loading) {
      if (!user) {
        navigate("/login");
      } else if (requireAdmin && !user.admin) {
        navigate("/"); // Redirect non-admins to home
      }
    }
  }, [user, loading, navigate, requireAdmin]);

  if (loading) return <p>Loading...</p>;

  if (!user || (requireAdmin && !user.admin)) {
    return null; // Already redirected
  }

  return <>{children}</>;
};

export default ProtectedRoute;
