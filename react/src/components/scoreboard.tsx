import React, { useEffect, useState } from "react";
import {
  API_BASE,   // newer API
} from "../api/api"; // adjust path if needed

type ScoreboardData = {
  time: string[];
  [team: string]: any[]; // dynamic keys like team0, team15 etc.
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

  // Extract team keys (exclude 'time')
  const teamKeys = Object.keys(data).filter((key) => key !== "time");

  // Get last index and previous index for last check points
  const lastIndex = data.time.length - 1;
  const prevIndex = lastIndex - 1 >= 0 ? lastIndex - 1 : 0;

  return (
    <div
      style={{
        margin: "40px auto",
        padding: "20px",
        maxWidth: "90%",
        width: "100%",
      }}
    >
      <section className="scoreboard-container">
      <h2 className="scoreboard-header">Scoreboard</h2>
      <p>Last update: {data.time[lastIndex]}</p>
      <table className="table table-striped table-dark">
        <thead>
          <tr>
            <th>Team</th>
            <th>Total Score</th>
            <th>Points Last Check</th>
          </tr>
        </thead>
        <tbody>
          {teamKeys.map((teamKey) => {
            const totalScore = data[teamKey][lastIndex];
            const prevScore = data[teamKey][prevIndex];
            const pointsLastCheck = totalScore - prevScore;

            return (
              <tr key={teamKey}>
                <td>{teamKey}</td>
                <td>{totalScore}</td>
                <td>{pointsLastCheck}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      </section>
    </div>
  );
};

export default Scoreboard;
