
import { BrowserRouter, Route, Routes, Link } from "react-router-dom";
import { AudioContext } from "./context";
import Landing from "./pages/Landing";
import Studio from "./pages/Studio";
import ChannelLab from "./pages/ChannelLab";
import SpeechLab from "./pages/SpeechLab";
import Compression from "./pages/Compression";
import Analytics from "./pages/Analytics";
import HistoryPage from "./pages/History";
import Research from "./pages/Research";
function Shell() {
  return (
    <div className="app-shell"><div className="main-shell"><main id="main"><Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/studio" element={<Studio />} />
            <Route path="/channel" element={<ChannelLab />} />
            <Route path="/speech" element={<SpeechLab />} />
            <Route path="/compression" element={<Compression />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/live" element={<Studio live />} />
            <Route path="/research" element={<Research />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route
              path="*"
              element={
                <div className="empty">
                  <h1>Page not found</h1>
                  <Link to="/">Return to laboratory</Link>
                </div>
              }
            />
          </Routes></main></div></div>
  );
}
export default function App() {
  return (
    <BrowserRouter>
      <AudioContext>
        <Shell />
      </AudioContext>
    </BrowserRouter>
  );
}