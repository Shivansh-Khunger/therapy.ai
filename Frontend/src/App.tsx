import Webcam from "react-webcam";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";


import Home from "./Home";
import WebFrame from "./WebFrame";
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/phy" element={<WebFrame/>} />
      </Routes>
    </Router>

  );
}

export default App;
