import React, { useState } from "react"
import Navbar from "../components/navbar";

const AdminPage: React.FC = () => { 
    return (
        <section className="dashboard-page-container">
            <Navbar admin={true}></Navbar>
            <div className="dashboard-content-cotnainer">
            </div>
        </section>
    );
};

export default AdminPage;
