import { useState, useEffect } from "react";
import { GlowDot } from "./indicators";

// ─── LIVE TICKER ──────────────────────────────────────────────────────────────
const LiveTicker = () => {
    const [tick, setTick] = useState(0);

    useEffect(() => {
        const i = setInterval(() => setTick(t => t + 1), 1000);
        return () => clearInterval(i);
    }, []);

    const s = tick % 60;

    return (
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#475569" }}>
            <GlowDot active={true} />
            <span style={{ color: "#22c55e", fontWeight: 600 }}>LIVE</span>
            <span>· Updates in {60 - s}s</span>
        </div>
    );
};

export default LiveTicker;
