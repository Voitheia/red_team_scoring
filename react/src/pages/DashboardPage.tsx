import React from "react";
import Navbar from "../components/navbar";
import Scoreboard from "../components/scoreboard";
import '../styles/App.css';
import { useAuth } from "../AuthContext";

const DashboardPage: React.FC = () => {
    const { user, logout } = useAuth();
  
    console.log("User from context:", user);
  
    if (!user) return <p>Loading user...</p>;
  
    return (
      <section className="dashboard-page-container">
        <Navbar admin={false} />
        <div className="dashboard-content-container">
          <div>
            <h1>Welcome, {user.username}</h1>
            <button onClick={logout}>Logout</button>
          </div>
          <Scoreboard />
        </div>
      </section>
    );
  };
  

export default DashboardPage;
