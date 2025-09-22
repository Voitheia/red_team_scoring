import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AppNavbar from "../components/navbar";
import Scoreboard from "../components/scoreboard";
import '../styles/App.css';
import { useAuth } from "../AuthContext";
import ProtectedRoute from "../components/protectedroute";

const DetailPage: React.FC = () => {
  return (
      <DetailContent />
  );
};

const DetailContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <div>
    <AppNavbar admin={user?.admin ?? false} />
    </div>
  );
};

export default DetailPage;
