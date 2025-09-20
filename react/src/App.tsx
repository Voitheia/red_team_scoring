import './styles/App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AdminPage from './pages/AdminPage'
import DashboardPage from './pages/DashboardPage';
import { AuthProvider } from './AuthContext';

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
    <AuthProvider>
      <AppWrapper />
    </AuthProvider>
  </Router>
);

export default App;
