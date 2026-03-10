import { pct } from "../utils";

// ─── SYNERGY INDICATOR ────────────────────────────────────────────────────────
const SynergyIndicator = ({ devices, combined }) => {
    const activeCount = [devices.vent, devices.cvc, devices.cath].filter(Boolean).length;
    if (activeCount < 2) return null;
    return (
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px", borderRadius: 10, background: "rgba(139,92,246,0.1)", border: "1px solid rgba(139,92,246,0.3)", marginTop: 8 }}>
            <span style={{ fontSize: 14 }}>⚡</span>
            <div>
                <div style={{ fontSize: 10, fontWeight: 700, color: "#a78bfa", letterSpacing: 0.8 }}>
                    {activeCount === 3 ? "TRIPLE DEVICE — MAX SYNERGY RISK" : "MULTI-DEVICE AMPLIFICATION ACTIVE"}
                </div>
                <div style={{ fontSize: 9, color: "#7c3aed" }}>Combined risk score: {pct(combined)}</div>
            </div>
        </div>
    );
};

export default SynergyIndicator;
