import { NavLink, Route, Routes, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Profile from "./pages/Profile.jsx";
import JDs from "./pages/JDs.jsx";
import Applications from "./pages/Applications.jsx";
import ApplicationDetail from "./pages/ApplicationDetail.jsx";

const navStyle = ({ isActive }) => (isActive ? "active" : "");

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Job Search Command Center</h1>
        <nav className="nav">
          <NavLink to="/" end className={navStyle}>Dashboard</NavLink>
          <NavLink to="/profile" className={navStyle}>Profile</NavLink>
          <NavLink to="/jds" className={navStyle}>Job Descriptions</NavLink>
          <NavLink to="/applications" className={navStyle}>Applications</NavLink>
        </nav>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/jds" element={<JDs />} />
          <Route path="/applications" element={<Applications />} />
          <Route path="/applications/:id" element={<ApplicationDetail />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
