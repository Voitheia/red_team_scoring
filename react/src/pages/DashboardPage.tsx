import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AppNavbar from "../components/navbar";
import Scoreboard from "../components/scoreboard";
import '../styles/App.css';
import { useAuth } from "../AuthContext";
import ProtectedRoute from "../components/protectedroute";

const DashboardPage: React.FC = () => {
  return (
      <DashboardContent />
  );
};

const DashboardContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <div>
    <AppNavbar admin={user?.admin ?? false} />
    <section className="dashboard-page-container">
        <Scoreboard />
    </section>
    </div>
  );
};

export default DashboardPage;
