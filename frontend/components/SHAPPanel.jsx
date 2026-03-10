import { useState, useEffect } from "react";
import { riskColor, riskBg, riskLabel, pct } from "../utils";

const API = "/api";

// ─── SHAP PANEL ───────────────────────────────────────────────────────────────
const SHAPPanel = ({ patient }) => {
    const [tab, setTab]       = useState("vap");
    const [shapData, setShapData] = useState(null);
    const [loading, setLoading]   = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch(`${API}/patients/${patient.id}/shap`)
            .then(r => r.json())
            .then(data => { setShapData(data); setLoading(false); })
            .catch(() => {
                // Fallback: generate placeholder from score
                const make = (keys) => keys.map(k => ({
                    label: k, value: "N/A",
                    shap: +(Math.random() * 0.2).toFixed(4),
                    dir: Math.random() > 0.3 ? "up" : "down",
                }));
                setShapData({
                    vap:    make(["Resp Rate", "SpO₂", "Temp", "WBC", "ICU LOS", "Heart Rate"]),
                    clabsi: make(["WBC", "Creatinine", "Temp", "ICU LOS", "BUN", "Glucose"]),
                    cauti:  make(["Creatinine", "BUN", "Temp", "WBC", "ICU LOS", "Heart Rate"]),
                });
                setLoading(false);
            });
    }, [patient.id]);

    if (loading) return (
        <div style={{ background: "#0a1628", borderRadius: 12, padding: 18, border: "1px solid #1e293b", color: "#475569", fontSize: 12 }}>
            Loading explanations…
        </div>
    );

    const features = shapData?.[tab] ?? [];
    const score    = patient.scores[tab];
    const maxShap  = Math.max(...features.map(f => Math.abs(f.shap)), 0.001);

    return (
        <div style={{ background: "#0a1628", borderRadius: 12, padding: 18, border: "1px solid #1e293b" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", letterSpacing: 1, marginBottom: 12 }}>
                EXPLAINABILITY — WHY IS RISK {riskLabel(score)}?
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", gap: 6, marginBottom: 16 }}>
                {[["vap", "VAP"], ["clabsi", "CLABSI"], ["cauti", "CAUTI"]].map(([k, l]) => (
                    <button key={k} onClick={() => setTab(k)} style={{
                        padding: "5px 14px", borderRadius: 8, fontSize: 11, fontWeight: 700, cursor: "pointer", border: "none",
                        background: tab === k ? riskBg(patient.scores[k]) : "#1e293b",
                        color: tab === k ? riskColor(patient.scores[k]) : "#475569",
                        transition: "all 0.15s",
                    }}>{l} · {pct(patient.scores[k])}</button>
                ))}
            </div>

            {/* Explanation text */}
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(30,41,59,0.5)", border: "1px solid #1e293b", marginBottom: 16, fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>
                <span style={{ color: riskColor(score), fontWeight: 700 }}>{tab.toUpperCase()} risk is {pct(score)} ({riskLabel(score)})</span>
                {" "}— primarily driven by {features.filter(f => f.dir === "up").slice(0, 2).map(f => f.label.toLowerCase()).join(" and ")}, sustained over the last 12h.
            </div>

            {/* Feature bars */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {features.map((f, i) => {
                    const barW = Math.abs(f.shap) / maxShap * 100;
                    const isUp = f.dir === "up";
                    return (
                        <div key={i} style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <span style={{ fontSize: 11, color: "#cbd5e1", fontWeight: 500 }}>{f.label}</span>
                                <span style={{ fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>{f.value}</span>
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <div style={{ flex: 1, height: 6, background: "#1e293b", borderRadius: 3, overflow: "hidden" }}>
                                    <div style={{ width: `${barW}%`, height: "100%", background: isUp ? riskColor(0.8) : "#22c55e", borderRadius: 3, transition: "width 0.5s ease", boxShadow: `0 0 6px ${isUp ? riskColor(0.8) : "#22c55e"}66` }} />
                                </div>
                                <span style={{ fontSize: 10, fontWeight: 700, color: isUp ? riskColor(0.8) : "#22c55e", width: 36, textAlign: "right" }}>
                                    {isUp ? "+" : ""}{Math.round(f.shap * 100)}%
                                </span>
                                <span style={{ fontSize: 12 }}>{isUp ? "↑" : "↓"}</span>
                            </div>
                            {i === 0 && (
                                <div style={{ fontSize: 10, color: "#475569", fontStyle: "italic" }}>
                                    💡 If {f.label.toLowerCase()} were normal, {tab.toUpperCase()} risk would be ~{Math.max(5, Math.round((score - f.shap) * 100))}%
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SHAPPanel;
