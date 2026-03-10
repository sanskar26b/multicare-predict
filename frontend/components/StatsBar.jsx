import { riskColor, pct } from "../utils";

// ─── STATS BAR ────────────────────────────────────────────────────────────────
const StatsBar = ({ patients, alerts }) => {
    const highRisk = patients.filter(p => p.scores.combined >= 0.7).length;
    const unacked = alerts.filter(a => !a.acked).length;
    const avgVAP = (patients.reduce((a, p) => a + p.scores.vap, 0) / patients.length);
    const stats = [
        { label: "Active Patients", value: patients.length, color: "#60a5fa", icon: "🏥" },
        { label: "High Risk", value: highRisk, color: highRisk > 0 ? "#ef4444" : "#22c55e", icon: "⚠️" },
        { label: "Unacked Alerts", value: unacked, color: unacked > 2 ? "#ef4444" : "#f59e0b", icon: "🔔" },
        { label: "Avg VAP Risk", value: pct(avgVAP), color: riskColor(avgVAP), icon: "📊" },
        { label: "Suppression Rate", value: "71%", color: "#22c55e", icon: "🛡️" },
    ];

    return (
        <div style={{ display: "flex", gap: 10 }}>
            {stats.map(s => (
                <div key={s.label} style={{ flex: 1, background: "rgba(15,23,42,0.8)", border: "1px solid #1e293b", borderRadius: 12, padding: "12px 16px", backdropFilter: "blur(8px)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                        <span style={{ fontSize: 14 }}>{s.icon}</span>
                        <span style={{ fontSize: 10, color: "#475569", fontWeight: 600, letterSpacing: 0.8 }}>{s.label.toUpperCase()}</span>
                    </div>
                    <div style={{ fontSize: 22, fontWeight: 800, color: s.color }}>{s.value}</div>
                </div>
            ))}
        </div>
    );
};

export default StatsBar;
