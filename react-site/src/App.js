import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/login";
import HomePage from "./pages/home";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;