// ─── DEVICE BADGE ─────────────────────────────────────────────────────────────
const DeviceBadge = ({ icon, label, hours, active }) => (
    <div style={{
        display: "flex", alignItems: "center", gap: 5, padding: "4px 10px", borderRadius: 8,
        background: active ? (hours > 72 ? "rgba(249,115,22,0.12)" : "rgba(59,130,246,0.12)") : "rgba(100,116,139,0.08)",
        border: `1px solid ${active ? (hours > 72 ? "#f9731622" : "#3b82f622") : "#334155"}`,
    }}>
        <span style={{ fontSize: 13 }}>{icon}</span>
        <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: active ? (hours > 72 ? "#f97316" : "#60a5fa") : "#475569", letterSpacing: 0.5 }}>{label}</div>
            {active && <div style={{ fontSize: 9, color: "#64748b" }}>{Math.floor(hours / 24)}d {hours % 24}h</div>}
            {!active && <div style={{ fontSize: 9, color: "#334155" }}>Inactive</div>}
        </div>
    </div>
);

export default DeviceBadge;
