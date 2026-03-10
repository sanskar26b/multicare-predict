import { useState, useEffect, useRef } from "react";
import LiveTicker from "./components/LiveTicker";
import StatsBar from "./components/StatsBar";
import PatientCard from "./components/PatientCard";
import PatientDetail from "./components/PatientDetail";
import AlertsSidebar from "./components/AlertsSidebar";

const API = "/api";

export default function App() {
  const [patients, setPatients]               = useState([]);
  const [alerts, setAlerts]                   = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [showAlerts, setShowAlerts]           = useState(false);
  const [filter, setFilter]                   = useState("all");
  const [view, setView]                       = useState("dashboard");
  const [loading, setLoading]                 = useState(true);
  const [error, setError]                     = useState(null);
  const wsRef = useRef(null);

  // ── Initial data fetch from backend ─────────────────────────────────────
  useEffect(() => {
    Promise.all([
      fetch(`${API}/patients`).then(r => r.json()),
      fetch(`${API}/alerts`).then(r => r.json()),
    ])
      .then(([pts, alts]) => { setPatients(pts); setAlerts(alts); setLoading(false); })
      .catch(() => {
        setError("Backend offline — showing demo data");
        import("./mockData").then(({ MOCK_PATIENTS, MOCK_ALERTS }) => {
          setPatients(MOCK_PATIENTS); setAlerts(MOCK_ALERTS); setLoading(false);
        });
      });
  }, []);

  // ── WebSocket live score updates ─────────────────────────────────────────
  useEffect(() => {
    if (loading) return;
    const connect = () => {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(`${protocol}://${window.location.host}/ws/live`);
      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === "score_update") {
            setPatients(prev => prev.map(p => {
              const upd = msg.data.find(u => u.id === p.id);
              return upd ? { ...p, scores: upd.scores } : p;
            }));
          }
        } catch (_) {}
      };
      ws.onclose = () => setTimeout(connect, 5000);
      wsRef.current = ws;
    };
    connect();
    return () => wsRef.current?.close();
  }, [loading]);

  // ── Alerts poll every 30 s ───────────────────────────────────────────────
  useEffect(() => {
    if (loading) return;
    const id = setInterval(() => {
      fetch(`${API}/alerts`).then(r => r.json()).then(setAlerts).catch(() => {});
    }, 30_000);
    return () => clearInterval(id);
  }, [loading]);

  const onAckAlert = (id) =>
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, acked: true } : a));
  const unackedCount = alerts.filter(a => !a.acked).length;

  const filteredPatients = patients
    .filter(p => filter === "all" ? true : filter === "high" ? p.scores.combined >= 0.5 : p.devices[filter])
    .sort((a, b) => b.scores.combined - a.scores.combined);

  const handlePatientClick = (p) => { setSelectedPatient(p); setView("detail"); };
  const handleBack         = ()  => { setView("dashboard"); setSelectedPatient(null); };

  // ── Loading screen ───────────────────────────────────────────────────────
  if (loading) return (
    <div style={{ minHeight: "100vh", background: "#060d1a", display: "flex", alignItems: "center", justifyContent: "center", color: "#64748b", fontFamily: "monospace", flexDirection: "column", gap: 16 }}>
      <div style={{ fontSize: 28 }}>⚡</div>
      <div style={{ fontSize: 13, letterSpacing: 2 }}>LOADING EDIPS…</div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: "#060d1a", fontFamily: "'IBM Plex Mono', 'Courier New', monospace", color: "#e2e8f0", position: "relative" }}>
      <div style={{ position: "fixed", inset: 0, backgroundImage: "linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px)", backgroundSize: "40px 40px", pointerEvents: "none" }} />

      {/* Navbar */}
      <div style={{ position: "sticky", top: 0, zIndex: 50, background: "rgba(6,13,26,0.95)", borderBottom: "1px solid #0f172a", backdropFilter: "blur(12px)", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 56 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg, #1d4ed8, #7c3aed)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>⚡</div>
            <span style={{ fontSize: 15, fontWeight: 800, color: "#e2e8f0", letterSpacing: 2 }}>EDIPS</span>
            <span style={{ fontSize: 10, color: "#334155", borderLeft: "1px solid #1e293b", paddingLeft: 10, letterSpacing: 1 }}>ICU SENTINEL v1.0</span>
          </div>
          {error
            ? <span style={{ fontSize: 10, color: "#f59e0b", padding: "2px 8px", background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.15)", borderRadius: 4 }}>⚠ {error}</span>
            : <span style={{ fontSize: 10, color: "#22c55e", padding: "2px 8px", background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.15)", borderRadius: 4 }}>● LIVE</span>
          }
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <LiveTicker />
          <button onClick={() => setShowAlerts(v => !v)} style={{ position: "relative", background: unackedCount > 0 ? "rgba(239,68,68,0.1)" : "#1e293b", border: `1px solid ${unackedCount > 0 ? "rgba(239,68,68,0.3)" : "#334155"}`, color: unackedCount > 0 ? "#ef4444" : "#94a3b8", padding: "6px 14px", borderRadius: 8, cursor: "pointer", fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            🔔 Alerts
            {unackedCount > 0 && <span style={{ background: "#ef4444", color: "#fff", fontSize: 9, fontWeight: 800, padding: "1px 5px", borderRadius: 10, minWidth: 16, textAlign: "center" }}>{unackedCount}</span>}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "20px 24px", position: "relative", zIndex: 1 }}>
        {view === "dashboard" && (
          <>
            <div style={{ marginBottom: 20 }}><StatsBar patients={patients} alerts={alerts} /></div>
            <div style={{ display: "flex", gap: 8, marginBottom: 20, alignItems: "center" }}>
              <span style={{ fontSize: 11, color: "#475569", letterSpacing: 1 }}>FILTER:</span>
              {[["all", "All Patients"], ["high", "High Risk (≥50%)"], ["vent", "Ventilated"], ["cvc", "CVC"], ["cath", "Catheter"]].map(([k, l]) => (
                <button key={k} onClick={() => setFilter(k)} style={{ padding: "5px 12px", borderRadius: 8, fontSize: 11, fontWeight: 600, cursor: "pointer", border: "none", background: filter === k ? "#1d4ed8" : "#1e293b", color: filter === k ? "#fff" : "#64748b", transition: "all 0.15s" }}>{l}</button>
              ))}
              <span style={{ marginLeft: "auto", fontSize: 11, color: "#334155" }}>{filteredPatients.length} patients shown</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 16 }}>
              {filteredPatients.map(p => <PatientCard key={p.id} patient={p} onClick={handlePatientClick} selected={false} />)}
            </div>
          </>
        )}
        {view === "detail" && selectedPatient && (
          <PatientDetail patient={patients.find(p => p.id === selectedPatient.id) || selectedPatient} onBack={handleBack} alerts={alerts} onAckAlert={onAckAlert} />
        )}
      </div>

      {showAlerts && (
        <>
          <div onClick={() => setShowAlerts(false)} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 90, backdropFilter: "blur(2px)" }} />
          <AlertsSidebar alerts={alerts} onAck={onAckAlert} onClose={() => setShowAlerts(false)} />
        </>
      )}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #060d1a; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }
        button:focus { outline: none; }
      `}</style>
    </div>
  );
}
