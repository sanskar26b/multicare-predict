import { riskColor, pct } from "../utils";

// ─── SCORE GAUGE ──────────────────────────────────────────────────────────────
const ScoreGauge = ({ score, label, size = "md" }) => {
    const r = size === "lg" ? 46 : 32;
    const stroke = size === "lg" ? 6 : 4.5;
    const circ = 2 * Math.PI * r;
    const filled = circ * score;
    const dim = (r + stroke) * 2 + 4;

    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
            <div style={{ position: "relative", width: dim, height: dim }}>
                <svg width={dim} height={dim} style={{ transform: "rotate(-90deg)" }}>
                    <circle cx={dim / 2} cy={dim / 2} r={r} fill="none" stroke="#1e293b" strokeWidth={stroke} />
                    <circle cx={dim / 2} cy={dim / 2} r={r} fill="none" stroke={riskColor(score)} strokeWidth={stroke}
                        strokeDasharray={`${filled} ${circ - filled}`} strokeLinecap="round"
                        style={{ filter: `drop-shadow(0 0 4px ${riskColor(score)}88)`, transition: "all 0.6s ease" }} />
                </svg>
                <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                    <span style={{ fontSize: size === "lg" ? 18 : 13, fontWeight: 800, color: riskColor(score), lineHeight: 1 }}>{pct(score)}</span>
                </div>
            </div>
            <span style={{ fontSize: 10, fontWeight: 600, color: "#64748b", letterSpacing: 1, textTransform: "uppercase" }}>{label}</span>
        </div>
    );
};

export default ScoreGauge;
