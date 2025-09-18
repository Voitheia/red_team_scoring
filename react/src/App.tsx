import './styles/App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AdminPage from './pages/AdminPage'
import DashboardPage from './pages/DashboardPage';

const AppWrapper = () => {
  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<DashboardPage />}/>
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </div>
  );
};

const App = () => (
  <Router>
    <AppWrapper />
  </Router>
);

export default App;
