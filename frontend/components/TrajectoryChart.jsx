import { useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import { generateTrajectory } from "../mockData";
import CustomTooltip from "./CustomTooltip";

// ─── TRAJECTORY CHART ─────────────────────────────────────────────────────────
const TrajectoryChart = ({ patientId, baseScore }) => {
    const [data] = useState(() => generateTrajectory(baseScore));
    const [range, setRange] = useState(24);
    const sliced = data.slice(-range);

    return (
        <div style={{ background: "#0a1628", borderRadius: 12, padding: "16px 16px 8px", border: "1px solid #1e293b" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", letterSpacing: 1 }}>RISK TRAJECTORY</span>
                <div style={{ display: "flex", gap: 4 }}>
                    {[24, 48, 72].map(h => (
                        <button key={h} onClick={() => setRange(h)} style={{
                            padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600, cursor: "pointer", border: "none",
                            background: range === h ? "#1d4ed8" : "#1e293b", color: range === h ? "#fff" : "#64748b",
                        }}>{h}h</button>
                    ))}
                </div>
            </div>

            {/* Legend */}
            <div style={{ display: "flex", gap: 12, marginBottom: 8 }}>
                {[["VAP", "#3b82f6"], ["CLABSI", "#f97316"], ["CAUTI", "#a855f7"]].map(([n, c]) => (
                    <div key={n} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        <span style={{ width: 16, height: 2, background: c, display: "inline-block", borderRadius: 2 }} />
                        <span style={{ fontSize: 10, color: "#64748b", fontWeight: 600 }}>{n}</span>
                    </div>
                ))}
            </div>

            <ResponsiveContainer width="100%" height={160}>
                <AreaChart data={sliced} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                    <defs>
                        <linearGradient id="gVAP" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} /><stop offset="95%" stopColor="#3b82f6" stopOpacity={0} /></linearGradient>
                        <linearGradient id="gCLABSI" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#f97316" stopOpacity={0.12} /><stop offset="95%" stopColor="#f97316" stopOpacity={0} /></linearGradient>
                        <linearGradient id="gCAUTI" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#a855f7" stopOpacity={0.12} /><stop offset="95%" stopColor="#a855f7" stopOpacity={0} /></linearGradient>
                    </defs>
                    <XAxis dataKey="h" tick={{ fontSize: 9, fill: "#334155" }} tickLine={false} axisLine={false} interval={Math.floor(range / 6)} />
                    <YAxis domain={[0, 1]} tick={{ fontSize: 9, fill: "#334155" }} tickLine={false} axisLine={false} tickFormatter={v => `${(v * 100).toFixed(0)}%`} />
                    <ReferenceLine y={0.7} stroke="#ef444422" strokeDasharray="3 3" />
                    <ReferenceLine y={0.45} stroke="#f59e0b22" strokeDasharray="3 3" />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="vap" stroke="#3b82f6" strokeWidth={2} fill="url(#gVAP)" dot={false} />
                    <Area type="monotone" dataKey="clabsi" stroke="#f97316" strokeWidth={2} fill="url(#gCLABSI)" dot={false} />
                    <Area type="monotone" dataKey="cauti" stroke="#a855f7" strokeWidth={2} fill="url(#gCAUTI)" dot={false} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TrajectoryChart;
