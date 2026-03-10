import AlertCard from "./AlertCard";

// ─── ALERTS SIDEBAR ───────────────────────────────────────────────────────────
const AlertsSidebar = ({ alerts, onAck, onClose }) => (
    <div style={{
        position: "fixed", right: 0, top: 0, bottom: 0, width: 380,
        background: "#0f172a", borderLeft: "1px solid #1e293b",
        boxShadow: "-20px 0 60px rgba(0,0,0,0.5)", zIndex: 100,
        display: "flex", flexDirection: "column",
    }}>
        <div style={{ padding: "18px 20px", borderBottom: "1px solid #1e293b", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0" }}>Alert Feed</div>
                <div style={{ fontSize: 11, color: "#64748b" }}>{alerts.filter(a => !a.acked).length} unacknowledged</div>
            </div>
            <button onClick={onClose} style={{ background: "#1e293b", border: "1px solid #334155", color: "#94a3b8", width: 32, height: 32, borderRadius: 8, cursor: "pointer", fontSize: 16 }}>×</button>
        </div>
        <div style={{ flex: 1, overflowY: "auto", padding: "12px 16px", display: "flex", flexDirection: "column", gap: 8 }}>
            {alerts.map(a => <AlertCard key={a.id} alert={a} onAck={onAck} />)}
        </div>
    </div>
);

export default AlertsSidebar;
