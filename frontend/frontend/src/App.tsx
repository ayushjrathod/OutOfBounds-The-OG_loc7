import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import Visualizations from "../../../app/vis/page";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/visualizations" element={<Visualizations />} />
      </Routes>
    </Router>
  );
}

export default App;
