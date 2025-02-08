import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Visualizations from './pages/Visualizations';

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
