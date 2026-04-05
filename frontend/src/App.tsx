
import { useEffect, useState } from "react";
import { BrowserRouter, NavLink, Route, Routes, Link, useLocation } from "react-router-dom";
import { AudioLines, Radio, FlaskConical, Languages, Layers3, ChartNoAxesCombined, MessagesSquare, GitBranch, History, Menu, X, ArrowUpRight } from "lucide-react";
import { api } from "./api";
import { AudioContext } from "./context";
import Landing from "./pages/Landing";
import Studio from "./pages/Studio";
import ChannelLab from "./pages/ChannelLab";
import SpeechLab from "./pages/SpeechLab";
import Compression from "./pages/Compression";
import Analytics from "./pages/Analytics";
import HistoryPage from "./pages/History";
import Research from "./pages/Research";
const navigation = [
  { to: "/", label: "Overview", icon: Layers3 },
  { to: "/studio", label: "Transceiver Studio", icon: Radio },
  { to: "/channel", label: "Channel Lab", icon: FlaskConical },
  { to: "/speech", label: "Speech Lab", icon: Languages },
  { to: "/compression", label: "Compression", icon: AudioLines },
  {
    to: "/analytics",
    label: "Performance Analytics",
    icon: ChartNoAxesCombined,
  },
  { to: "/live", label: "Live Demo", icon: MessagesSquare },
  { to: "/research", label: "Research & Architecture", icon: GitBranch },
  { to: "/history", label: "Experiment History", icon: History },
];
function Shell() {
  const [online, setOnline] = useState<boolean | null>(null);
  const [open, setOpen] = useState(false);
  const location = useLocation();
  useEffect(() => {
    setOpen(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  useEffect(() => {
    let alive = true;
    const check = () => {
      void api("/health")
        .then(() => {
          if (alive) setOnline(true);
        })
        .catch(() => {
          if (alive) setOnline(false);
        });
    };
    check();
    const timer = setInterval(check, 15000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);
  return (
    <div className="app-shell"><aside className={"sidebar " + (open ? "open" : "")}>
        <Link to="/" className="brand">
          <span className="brand-mark">
            <AudioLines size={25} />
          </span>
          <div>
            iTantra<small>NEURAL COMMUNICATION LAB</small>
          </div>
        </Link>
        <span className="nav-label">WORKSPACE</span>
        <nav>
          {navigation.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.to === "/"}>
              <n.icon size={18} />
              {n.label}
              {n.to === "/studio" && <span className="nav-dot" />}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="local-badge">
            <i />
            LOCAL RESEARCH ENVIRONMENT
          </div>
          <p>
            Speech stays on this machine.
            <br />
            No cloud inference. No physical RF.
          </p>
          <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
            API documentation <ArrowUpRight size={14} />
          </a>
          <div className="sidebar-version">
            iTantra v1.0 <span>CPU READY</span>
          </div>
        </div>
      </aside>{open && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        />
      )}<div className="main-shell"><div className="topbar">
          <button
            className="menu-toggle"
            aria-label="Toggle navigation"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X /> : <Menu />}
          </button>
          <div className="breadcrumb">
            LABORATORY <span>/</span>{" "}
            {navigation
              .find((n) => n.to === location.pathname)
              ?.label.toUpperCase() || "OVERVIEW"}
          </div>
          <div className="topbar-status">
            <span className="simulation-label">SOFTWARE SIMULATION</span>
            <span
              className={
                "connection " +
                (online === null ? "pending" : online ? "online" : "")
              }
            >
              <i />
              {online === null
                ? "Connecting backend"
                : online
                  ? "Backend connected"
                  : "Backend offline"}
            </span>
            <span className="avatar">IT</span>
          </div>
        </div><main id="main"><Routes>
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
          </Routes><footer>
            <span>
              iTantra / Indian Multilingual Neural Voice Communication
            </span>
            <span>MEASURED. REPRODUCIBLE. LOCAL.</span>
          </footer></main></div></div>
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