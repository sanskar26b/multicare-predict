import { riskColor, pct } from "../utils";
import ScoreGauge from "./ScoreGauge";
import { RiskPill } from "./indicators";
import SynergyIndicator from "./SynergyIndicator";
import DeviceBadge from "./DeviceBadge";
import VitalsStrip from "./VitalsStrip";
import TrajectoryChart from "./TrajectoryChart";
import SHAPPanel from "./SHAPPanel";
import AlertCard from "./AlertCard";

// ─── PATIENT DETAIL ───────────────────────────────────────────────────────────
const PatientDetail = ({ patient, onBack, alerts, onAckAlert }) => {
    const patientAlerts = alerts.filter(a => a.patientId === patient.id);

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Back + Header */}
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <button onClick={onBack} style={{ background: "#1e293b", border: "1px solid #334155", color: "#94a3b8", padding: "6px 14px", borderRadius: 8, cursor: "pointer", fontSize: 12 }}>← Back</button>
                <div>
                    <span style={{ fontFamily: "monospace", fontSize: 18, fontWeight: 800, color: "#e2e8f0", letterSpacing: 1 }}>{patient.id}</span>
                    <span style={{ fontSize: 12, color: "#64748b", marginLeft: 12 }}>{patient.age}y {patient.gender} · {patient.unit} · ICU Day {patient.dayInICU}</span>
                </div>
                <RiskPill score={patient.scores.combined} label={`Combined ${pct(patient.scores.combined)}`} />
            </div>

            {/* Risk Gauges */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                {[["vap", "VAP", "Ventilator-Associated Pneumonia"], ["clabsi", "CLABSI", "Bloodstream Infection"], ["cauti", "CAUTI", "Urinary Tract Infection"]].map(([k, l, full]) => (
                    <div key={k} style={{ background: "#0a1628", border: `1px solid ${riskColor(patient.scores[k])}22`, borderRadius: 14, padding: "20px 16px", display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
                        <ScoreGauge score={patient.scores[k]} label={l} size="lg" />
                        <div style={{ fontSize: 10, color: "#475569", textAlign: "center" }}>{full}</div>
                        <RiskPill score={patient.scores[k]} />
                    </div>
                ))}
            </div>

            {/* Synergy */}
            <SynergyIndicator devices={patient.devices} combined={patient.scores.combined} />

            {/* Devices */}
            <div style={{ background: "#0a1628", borderRadius: 12, padding: 16, border: "1px solid #1e293b" }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", letterSpacing: 1, marginBottom: 12 }}>ACTIVE DEVICES</div>
                <div style={{ display: "flex", gap: 10 }}>
                    <DeviceBadge icon="🫁" label="Ventilator" hours={patient.devices.ventHours} active={patient.devices.vent} />
                    <DeviceBadge icon="💉" label="Central Line" hours={patient.devices.cvcHours} active={patient.devices.cvc} />
                    <DeviceBadge icon="🔵" label="Urinary Catheter" hours={patient.devices.cathHours} active={patient.devices.cath} />
                </div>
            </div>

            {/* Vitals */}
            <div style={{ background: "#0a1628", borderRadius: 12, padding: 16, border: "1px solid #1e293b" }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", letterSpacing: 1, marginBottom: 12 }}>CURRENT VITALS</div>
                <VitalsStrip vitals={patient.vitals} />
            </div>

            {/* Trajectory */}
            <TrajectoryChart patientId={patient.id} baseScore={patient.scores.combined} />

            {/* SHAP */}
            <SHAPPanel patient={patient} />

            {/* Alerts */}
            {patientAlerts.length > 0 && (
                <div style={{ background: "#0a1628", borderRadius: 12, padding: 16, border: "1px solid #1e293b" }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", letterSpacing: 1, marginBottom: 12 }}>ACTIVE ALERTS</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                        {patientAlerts.map(a => <AlertCard key={a.id} alert={a} onAck={onAckAlert} />)}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PatientDetail;
