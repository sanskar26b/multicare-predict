// ─── VITALS STRIP ─────────────────────────────────────────────────────────────
const VitalsStrip = ({ vitals }) => {
    const items = [
        { label: "HR", value: vitals.hr, unit: "bpm", normal: [60, 100], color: "#22c55e" },
        { label: "Temp", value: vitals.temp, unit: "°C", normal: [36.1, 37.9], color: "#f97316" },
        { label: "SpO₂", value: vitals.spo2, unit: "%", normal: [95, 100], color: "#3b82f6" },
        { label: "RR", value: vitals.rr, unit: "/min", normal: [12, 20], color: "#a855f7" },
        { label: "BP", value: vitals.bp, unit: "", normal: null, color: "#94a3b8" },
    ];

    return (
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {items.map(({ label, value, unit, normal, color }) => {
                const abnormal = normal && (value < normal[0] || value > normal[1]);
                return (
                    <div key={label} style={{
                        flex: "1 1 80px", background: "#0a1628",
                        border: `1px solid ${abnormal ? "#ef444433" : "#1e293b"}`,
                        borderRadius: 10, padding: "10px 14px", textAlign: "center",
                    }}>
                        <div style={{ fontSize: 9, color: "#475569", fontWeight: 700, letterSpacing: 1, marginBottom: 4 }}>{label}</div>
                        <div style={{ fontSize: 20, fontWeight: 800, color: abnormal ? "#ef4444" : color, lineHeight: 1 }}>{value}</div>
                        <div style={{ fontSize: 9, color: "#334155", marginTop: 2 }}>{unit}</div>
                    </div>
                );
            })}
        </div>
    );
};

export default VitalsStrip;
