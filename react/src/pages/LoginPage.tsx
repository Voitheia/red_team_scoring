import React, { useState } from "react"
import { Link, useNavigate } from "react-router-dom";
import '../styles/Login.css'
import { login } from "../api/api";

const Login: React.FC = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!username || !password) {
            setError("Please enter both username and password.");
            return;
        }

        setError("");
        try {
            const data = await login(username, password);
            console.log("Login successful:", data);
            localStorage.setItem("authToken", data.token);
            navigate('/'); 
        } catch (err: any) {
            setError(err.message || "Invalid credentials.");
        }
    };

    return (
        <div className="login-page-container">
            <h2 className="login-page-header">Login</h2>
            <form className="login-form-container" onSubmit={handleLogin}>
                <input
                    type="username"
                    placeholder="Username"
                    className="login-form-username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                /><br />
                <input
                    type="password"
                    placeholder="Password"
                    className="login-form-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                /><br />
                <button className="login-form-button" type="submit">Login</button>
                {error && <p className="login-form-error" style={{ color: "red" }}>{error}</p>}
            </form>
        </div>
    );
};

export default Login;
