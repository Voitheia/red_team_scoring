import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AppNavbar from "../components/navbar";
import Scoreboard from "../components/scoreboard";
import '../styles/App.css';
import { useAuth } from "../AuthContext";
import ProtectedRoute from "../components/protectedroute";
import { getDetails } from "../api/api";

const DetailPage: React.FC = () => {
  return (
    <ProtectedRoute>
      <DetailContent />
    </ProtectedRoute>
  );
};

type IocDetail = {
  team_num: number;
  box_ip: string;
  ioc_name: string;
  difficulty: number;
  status: number;
  error: string | null;
  points: number;
};

const DetailContent: React.FC = () => {
  const [details, setDetails] = useState<IocDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getDetails();
        setDetails(data.details);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <p>Loading IOC details...</p>;
  if (error) return <p className="text-danger">Error: {error}</p>;

  return (
    <div>
    <AppNavbar admin={false} />
    <div className="container mt-4">
      <h2>Team IOC Details</h2>
      <table className="table table-striped table-dark table-sm">
        <thead>
          <tr>
            <th>Team</th>
            <th>Box</th>
            <th>IOC</th>
            <th>Difficulty</th>
            <th>Status</th>
            <th>Points</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          {details.map((d) => (
            <tr key={`${d.team_num}-${d.box_ip}-${d.ioc_name}`}>
              <td>{d.team_num}</td>
              <td>{d.box_ip}</td>
              <td>{d.ioc_name}</td>
              <td>{d.difficulty}</td>
              <td>{d.status === 0 ? "✅ Pass" : "❌ Fail"}</td>
              <td>{d.points}</td>
              <td>{d.error || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </div>
  );
};

export default DetailPage;

