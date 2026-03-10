import { pct } from "../utils";

// ─── CUSTOM TOOLTIP ───────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 10, padding: "10px 14px", fontSize: 12 }}>
            <div style={{ color: "#64748b", marginBottom: 6, fontWeight: 600 }}>{label}</div>
            {payload.map(p => (
                <div key={p.dataKey} style={{ color: p.color, display: "flex", gap: 8 }}>
                    <span style={{ textTransform: "uppercase", fontSize: 10, width: 50 }}>{p.dataKey}</span>
                    <span style={{ fontWeight: 700 }}>{pct(p.value)}</span>
                </div>
            ))}
        </div>
    );
};

export default CustomTooltip;
