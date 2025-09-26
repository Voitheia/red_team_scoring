import React, { useEffect, useState } from "react";
import {
  API_BASE,   // newer API
} from "../api/api"; // adjust path if needed

type TeamEntry = {
  team_num: number;
  total_score: number;
  last_check_score: number;
  last_check_time: string | null;
};

type ScoreboardData = {
  teams: TeamEntry[];
};

const Scoreboard: React.FC = () => {
  const [data, setData] = useState<ScoreboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchScoreboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_BASE + "/scoreboard");
      if (!response.ok) {
        throw new Error(`Failed to fetch scoreboard: ${response.statusText}`);
      }
      const jsonData: ScoreboardData = await response.json();
      setData(jsonData);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScoreboard();
    const interval = setInterval(fetchScoreboard, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <p>Loading scoreboard...</p>;
  if (error) return <p className="text-danger">Error: {error}</p>;
  if (!data) return null;

  return (
    <div style={{ margin: "40px auto", padding: "20px", maxWidth: "90%", width: "100%" }}>
      <section className="scoreboard-container">
        <h2 className="scoreboard-header">Scoreboard</h2>
        <table className="table table-striped table-dark">
          <thead>
            <tr>
              <th>Team</th>
              <th>Total Score</th>
              <th>Points Last Check</th>
              <th>Last Check Time</th>
            </tr>
          </thead>
          <tbody>
            {data.teams.map((team) => (
              <tr key={team.team_num}>
                <td>{`Team ${team.team_num}`}</td>
                <td>{team.total_score}</td>
                <td>{team.last_check_score}</td>
                <td>{team.last_check_time ? new Date(team.last_check_time).toLocaleTimeString() : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default Scoreboard;
