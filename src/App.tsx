// import { PrimeReactProvider } from 'primereact/api';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { AdminPage } from "./Pages/AdminPage";

export default function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          {/* Redirect root path to login */}
          <Route path="/" element={<Navigate to="/admin/chat" />} />
          {/* Login Page */}
          <Route path="/admin/*" element={<AdminPage />} />
          {/* <Route path="*" element={<NotFoundPage />} /> */}
        </Routes>
      </Router>
    </div>
  );
}
