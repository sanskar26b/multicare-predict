import { riskColor, riskBg, riskLabel, pct } from "../utils";
import { RiskPill } from "./indicators";
import ScoreGauge from "./ScoreGauge";
import DeviceBadge from "./DeviceBadge";
import SynergyIndicator from "./SynergyIndicator";

// ─── PATIENT CARD ─────────────────────────────────────────────────────────────
const PatientCard = ({ patient, onClick, selected }) => {
    const { id, age, gender, unit, dayInICU, devices, scores, trend } = patient;
    return (
        <div onClick={() => onClick(patient)} style={{
            background: selected ? "rgba(30,41,59,0.95)" : "rgba(15,23,42,0.8)",
            border: `1px solid ${selected ? "#3b82f6" : scores.combined >= 0.7 ? "#ef444433" : "#1e293b"}`,
            borderRadius: 16, padding: "18px 20px", cursor: "pointer",
            transition: "all 0.2s ease", backdropFilter: "blur(8px)",
            boxShadow: selected ? "0 0 0 2px #3b82f640" : scores.combined >= 0.7 ? "0 0 20px rgba(239,68,68,0.08)" : "none",
        }}
            onMouseEnter={e => { if (!selected) e.currentTarget.style.borderColor = "#334155"; }}
            onMouseLeave={e => { if (!selected) e.currentTarget.style.borderColor = scores.combined >= 0.7 ? "#ef444433" : "#1e293b"; }}
        >
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontFamily: "'Courier New', monospace", fontSize: 14, fontWeight: 700, color: "#e2e8f0", letterSpacing: 1 }}>{id}</span>
                        {trend === "rising" && <span style={{ fontSize: 9, color: "#ef4444", background: "rgba(239,68,68,0.1)", padding: "1px 6px", borderRadius: 4, fontWeight: 700 }}>↑ RISING</span>}
                    </div>
                    <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>{age}y {gender} · {unit} · Day {dayInICU}</div>
                </div>
                <RiskPill score={scores.combined} />
            </div>

            {/* Devices */}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 14 }}>
                <DeviceBadge icon="🫁" label="Ventilator" hours={devices.ventHours} active={devices.vent} />
                <DeviceBadge icon="💉" label="Central Line" hours={devices.cvcHours} active={devices.cvc} />
                <DeviceBadge icon="🔵" label="Catheter" hours={devices.cathHours} active={devices.cath} />
            </div>

            {/* Scores */}
            <div style={{ display: "flex", justifyContent: "space-around", padding: "12px 0", borderTop: "1px solid #1e293b", borderBottom: "1px solid #1e293b", marginBottom: 12 }}>
                <ScoreGauge score={scores.vap} label="VAP" />
                <ScoreGauge score={scores.clabsi} label="CLABSI" />
                <ScoreGauge score={scores.cauti} label="CAUTI" />
            </div>

            <SynergyIndicator devices={devices} combined={scores.combined} />
        </div>
    );
};

export default PatientCard;
