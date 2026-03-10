import { riskColor } from "../utils";

// ─── GLOW DOT ─────────────────────────────────────────────────────────────────
export const GlowDot = ({ active }) => (
    <span style={{
        display: "inline-block", width: 8, height: 8, borderRadius: "50%",
        background: active ? "#22c55e" : "#ef4444",
        boxShadow: active ? "0 0 8px #22c55e" : "0 0 8px #ef4444",
        marginRight: 6,
    }} />
);

// ─── RISK PILL ────────────────────────────────────────────────────────────────
import { riskBg, riskLabel } from "../utils";

export const RiskPill = ({ score, label }) => (
    <span style={{
        display: "inline-flex", alignItems: "center", gap: 5,
        padding: "3px 10px", borderRadius: 20,
        background: riskBg(score), border: `1px solid ${riskColor(score)}33`,
        fontSize: 11, fontWeight: 700, color: riskColor(score), letterSpacing: 1,
    }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: riskColor(score), boxShadow: `0 0 6px ${riskColor(score)}` }} />
        {label || riskLabel(score)}
    </span>
);
