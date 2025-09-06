// react-site/src/pages/home.js

import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function HomePage() {
  return (
    <div className="bg-light min-vh-100 d-flex flex-column">
      {/* Hero Section */}
      <header className="bg-primary text-white text-center py-5 shadow-sm">
        <div className="container">
          <h1 className="display-4 fw-bold">Red Team Scoring System</h1>
          <p className="lead">Track blue team performance in real time.</p>
          <Link to="/login" className="btn btn-outline-light btn-lg mt-3">
            Get Started
          </Link>
        </div>
      </header>

      {/* Features Section */}
      <section className="py-5">
        <div className="container text-center">
          <div className="row g-4">
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow">
                <div className="card-body">
                  <i className="bi bi-shield-lock display-4 text-primary mb-3"></i>
                  <h5 className="card-title">Secure Access</h5>
                  <p className="card-text">Only authorized users can log in and view team data.</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow">
                <div className="card-body">
                  <i className="bi bi-graph-up display-4 text-success mb-3"></i>
                  <h5 className="card-title">Live Scoreboard</h5>
                  <p className="card-text">Scores update in real time as check results come in.</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card h-100 border-0 shadow">
                <div className="card-body">
                  <i className="bi bi-tools display-4 text-warning mb-3"></i>
                  <h5 className="card-title">Custom Checks</h5>
                  <p className="card-text">Support for tailored IOC checks per team environment.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-4 bg-dark text-white text-center">
        <div className="container">
          <small>© {new Date().getFullYear()} Red Team Scoring. All rights reserved.</small>
        </div>
      </footer>
    </div>
  );
}

export default HomePage;
