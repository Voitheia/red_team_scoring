import React, { useState, useEffect } from "react";
import {
  deployIOCs,
  runChecks,
  startCompetition,
  stopCompetition,
  getSystemStatus,
  resetCompetitionData,
} from "../api/api"; // adjust path if needed
import AppNavbar from "../components/navbar";
import ProtectedRoute from "../components/protectedroute";

const AdminPage: React.FC = () => {
  return (
    <ProtectedRoute requireAdmin>
      <AppNavbar admin={false} />
      <section className="dashboard-page-container">
        <div className="dashboard-content-container">
          <AdminController />
        </div>
      </section>
    </ProtectedRoute>
  );
};


const AdminController: React.FC = () => {
    const [status, setStatus] = useState<string>("");
    const [systemStatus, setSystemStatus] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const fetchStatus = async () => {
      try {
        const statusData = await getSystemStatus();
        setSystemStatus(statusData);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to fetch system status");
      }
    };
  
    useEffect(() => {
        fetchStatus(); // initial fetch
      
        const intervalId = setInterval(() => {
          fetchStatus();
        }, 5000); // fetch every 5 seconds
      
        // Cleanup interval on unmount
        return () => clearInterval(intervalId);
      }, []);
      
  
    const handleAction = async (action: () => Promise<any>, successMsg: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await action();
        setStatus(successMsg);
        // Update system status after action
        await fetchStatus();
      } catch (err: any) {
        setError(err.message || "Action failed");
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div className="admin-controller">
        <h2>Admin Controls</h2>
  
        <div className="buttons">
          <button
            disabled={loading}
            onClick={() => handleAction(startCompetition, "Competition started")}
            className="btn btn-success me-2"
          >
            Start Competition
          </button>
  
          <button
            disabled={loading}
            onClick={() => handleAction(stopCompetition, "Competition stopped")}
            className="btn btn-danger me-2"
          >
            Stop Competition
          </button>
  
          <button
            disabled={loading}
            onClick={() => handleAction(resetCompetitionData, "Competition data reset")}
            className="btn btn-warning me-2"
          >
            Reset Data
          </button>
  
          <button
            disabled={loading}
            onClick={() => handleAction(deployIOCs, "IOCs deployed")}
            className="btn btn-primary me-2"
          >
            Deploy IOCs
          </button>
  
          <button
            disabled={loading}
            onClick={() => handleAction(runChecks, "Checks run")}
            className="btn btn-info me-2"
          >
            Run Checks
          </button>
        </div>
  
        {loading && <p>Loading...</p>}
  
        {status && <p className="text-success mt-2">{status}</p>}
        {error && <p className="text-danger mt-2">{error}</p>}
  
        <h3 className="mt-4">System Status</h3>
        <pre
            style={{
                maxHeight: "300px",
                overflowY: "auto",
                padding: "1rem",
                border: "1px solid #ddd",
                borderRadius: "4px",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                fontFamily: "monospace",
            }}
            >
            {systemStatus ? JSON.stringify(systemStatus, null, 2) : "No status available"}
        </pre>

      </div>
    );
  };
  

export default AdminPage;
