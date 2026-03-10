// ─── UTILS ────────────────────────────────────────────────────────────────────
export const riskColor = (s) => s >= 0.7 ? "#ef4444" : s >= 0.45 ? "#f59e0b" : "#22c55e";
export const riskBg = (s) => s >= 0.7 ? "rgba(239,68,68,0.12)" : s >= 0.45 ? "rgba(245,158,11,0.12)" : "rgba(34,197,94,0.12)";
export const riskLabel = (s) => s >= 0.7 ? "HIGH" : s >= 0.45 ? "MED" : "LOW";
export const pct = (s) => Math.round(s * 100) + "%";
