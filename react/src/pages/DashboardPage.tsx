import React from "react"
import Navbar from "../components/navbar";
import Scoreboard from "../components/scoreboard";
import '../styles/App.css'

const DashboardPage: React.FC = () => {
    return (
        <section className="dashboard-page-container">
            <Navbar admin={false}></Navbar>
            <div className="dashboard-content-cotnainer">
                <Scoreboard></Scoreboard>
            </div>
        </section>
    );
};

export default DashboardPage;
