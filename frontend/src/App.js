import "./App.css";
import Schedule from "./components/admin/Schedule";
import Login from "./components/common/Login";
import { Routes, Route, Link } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/finance/dashboard" element={<Schedule />} />
      </Routes>
    </div>
  );
}

export default App;
