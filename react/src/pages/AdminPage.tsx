// src/pages/AdminPage.tsx

import React, { useState, useEffect } from "react";
import {
  deployIOCs,
  runChecks,
  startCompetition,
  stopCompetition,
  getSystemStatus,
  resetCompetitionData,
  getUsers,        // new API
  removeUser,      // new API
  addUser          // new API
} from "../api/api"; // adjust path if needed
import AppNavbar from "../components/navbar";
import ProtectedRoute from "../components/protectedroute";
import { Button, Table, Modal, Form } from "react-bootstrap";

type User = {
  user_id: number;
  username: string;
  is_admin: boolean;
  is_blue_team: boolean;
  blue_team_num: number | null;
};

const AdminPage: React.FC = () => {
  return (
    <ProtectedRoute requireAdmin>
      <AppNavbar admin={false} />
      <section className="dashboard-page-container">
        <div className="dashboard-content-container">
          <AdminController />
          <hr />
          <ManageUsers />
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
    <div className="admin-controller mb-4">
      <h2>Admin Controls</h2>

      <div className="buttons mb-3">
        <Button
          disabled={loading}
          onClick={() => handleAction(startCompetition, "Competition started")}
          variant="success"
          className="me-2"
        >
          Start Competition
        </Button>

        <Button
          disabled={loading}
          onClick={() => handleAction(stopCompetition, "Competition stopped")}
          variant="danger"
          className="me-2"
        >
          Stop Competition
        </Button>

        <Button
          disabled={loading}
          onClick={() => handleAction(resetCompetitionData, "Competition data reset")}
          variant="warning"
          className="me-2"
        >
          Reset Data
        </Button>

        <Button
          disabled={loading}
          onClick={() => handleAction(deployIOCs, "IOCs deployed")}
          variant="primary"
          className="me-2"
        >
          Deploy IOCs
        </Button>

        <Button
          disabled={loading}
          onClick={() => handleAction(runChecks, "Checks run")}
          variant="info"
          className="me-2"
        >
          Run Checks
        </Button>
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

const ManageUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  const [newUser, setNewUser] = useState<Partial<User> & { password?: string }>({
    user_id: 0,
    username: "",
    is_admin: false,
    is_blue_team: false,
    blue_team_num: null,
    password: "",
  });

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await getUsers();
      setUsers(resp.users);
    } catch (err: any) {
      setError(err.message || "Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleDelete = async (user_id: number) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await removeUser({ user_id });
      fetchUsers();  // refresh after delete
    } catch (err: any) {
      alert("Delete failed: " + (err.message || err));
    }
  };

  const handleAddUser = async () => {
    // Validate inputs
    if (!newUser.username || !newUser.password) {
      alert("Please fill username, and password");
      return;
    }
    try {
      await addUser({
        user_id: newUser.user_id!,
        username: newUser.username!,
        password: newUser.password!,
        is_admin: newUser.is_admin!,
        is_blue_team: newUser.is_blue_team!,
        blue_team_num: newUser.is_blue_team ? newUser.blue_team_num : null,
      });
      setShowAddModal(false);
      fetchUsers();
      // Reset form
      setNewUser({
        user_id: 0,
        username: "",
        is_admin: false,
        is_blue_team: false,
        blue_team_num: null,
        password: "",
      });
    } catch (err: any) {
      alert("Add user failed: " + (err.message || err));
    }
  };

  return (
    <div className="manage-users">
      <h2>Manage Users</h2>
      {loading && <p>Loading users...</p>}
      {error && <p className="text-danger">Error: {error}</p>}
      {!loading && (
        <>
          <Button onClick={() => setShowAddModal(true)} variant="primary" className="mb-3">
            Add User
          </Button>
          <Table striped variant="dark" bordered hover size="sm">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Admin</th>
                <th>Blue Team</th>
                <th>Team Number</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.user_id}>
                  <td>{u.user_id}</td>
                  <td>{u.username}</td>
                  <td>{u.is_admin ? "Yes" : "No"}</td>
                  <td>{u.is_blue_team ? "Yes" : "No"}</td>
                  <td>{u.is_blue_team && u.blue_team_num != null ? u.blue_team_num : "-"}</td>
                  <td>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(u.user_id)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </>
      )}

      <Modal show={showAddModal} onHide={() => setShowAddModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add User</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-2">
              <Form.Label>User ID</Form.Label>
              <Form.Control
                type="number"
                value={newUser.user_id}
                onChange={(e) => setNewUser({ ...newUser, user_id: Number(e.target.value) })}
              />
            </Form.Group>
            <Form.Group className="mb-2">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-2">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-2">
              <Form.Check
                type="checkbox"
                label="Is Admin?"
                checked={newUser.is_admin || false}
                onChange={(e) => setNewUser({ ...newUser, is_admin: e.target.checked })}
              />
            </Form.Group>
            <Form.Group className="mb-2">
              <Form.Check
                type="checkbox"
                label="Is Blue Team?"
                checked={newUser.is_blue_team || false}
                onChange={(e) => {
                  setNewUser({ 
                    ...newUser, 
                    is_blue_team: e.target.checked,
                    blue_team_num: null,
                  });
                }}
              />
            </Form.Group>
            {newUser.is_blue_team && (
              <Form.Group className="mb-2">
                <Form.Label>Blue Team Number</Form.Label>
                <Form.Control
                  type="number"
                  value={newUser.blue_team_num || ""}
                  onChange={(e) =>
                    setNewUser({ ...newUser, blue_team_num: Number(e.target.value) })
                  }
                />
              </Form.Group>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleAddUser}>
            Add
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default AdminPage;
