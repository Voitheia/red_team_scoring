import './styles/App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AdminPage from './pages/AdminPage'
import DashboardPage from './pages/DashboardPage';
import { AuthProvider } from './AuthContext';
import DetailPage from './pages/DetailPage';



const AppWrapper = () => {
  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<DashboardPage />}/>
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/details" element={<DetailPage />}/>
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
