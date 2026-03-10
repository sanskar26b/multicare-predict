import { useState } from "react";
import { riskColor, pct } from "../utils";

// ─── ALERT CARD ───────────────────────────────────────────────────────────────
const AlertCard = ({ alert, onAck }) => {
    const [acked, setAcked] = useState(alert.acked);
    return (
        <div style={{
            padding: "12px 16px", borderRadius: 10, border: `1px solid ${acked ? "#1e293b" : alert.level === "RED" ? "#ef444422" : "#f59e0b22"}`,
            borderLeft: `3px solid ${acked ? "#334155" : alert.level === "RED" ? "#ef4444" : "#f59e0b"}`,
            background: acked ? "rgba(15,23,42,0.4)" : "rgba(15,23,42,0.8)", opacity: acked ? 0.6 : 1,
            transition: "all 0.3s",
        }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <span style={{ fontSize: 11, fontWeight: 800, color: alert.level === "RED" ? "#ef4444" : "#f59e0b", letterSpacing: 1 }}>
                            {alert.level === "RED" ? "🔴" : "🟡"} {alert.type}
                        </span>
                        <span style={{ fontFamily: "monospace", fontSize: 11, color: "#64748b" }}>{alert.patientId}</span>
                        <span style={{ fontSize: 10, color: "#475569" }}>{alert.time}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "#94a3b8", lineHeight: 1.5 }}>{alert.explanation}</div>
                    <div style={{ fontSize: 10, color: "#475569", marginTop: 4 }}>Score: <span style={{ color: riskColor(alert.score), fontWeight: 700 }}>{pct(alert.score)}</span></div>
                </div>
                {!acked && (
                    <button onClick={() => { setAcked(true); onAck(alert.id); }} style={{
                        marginLeft: 12, padding: "4px 12px", borderRadius: 6, background: "#1e293b", border: "1px solid #334155",
                        color: "#94a3b8", fontSize: 11, cursor: "pointer", whiteSpace: "nowrap",
                    }}>Acknowledge</button>
                )}
                {acked && <span style={{ fontSize: 10, color: "#334155", marginLeft: 12 }}>✓ Acked</span>}
            </div>
        </div>
    );
};

export default AlertCard;
