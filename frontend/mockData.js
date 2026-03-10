// ─── MOCK DATA ────────────────────────────────────────────────────────────────
export const MOCK_PATIENTS = [
    {
        id: "ICU-1042", age: 67, gender: "M", unit: "MICU", dayInICU: 6,
        devices: { vent: true, ventHours: 144, cvc: true, cvcHours: 120, cath: true, cathHours: 96 },
        scores: { vap: 0.78, clabsi: 0.61, cauti: 0.44, combined: 0.74 },
        vitals: { hr: 102, temp: 38.6, spo2: 94, rr: 22, bp: "118/74" },
        trend: "rising",
    },
    {
        id: "ICU-0891", age: 54, gender: "F", unit: "SICU", dayInICU: 3,
        devices: { vent: true, ventHours: 72, cvc: true, cvcHours: 68, cath: false, cathHours: 0 },
        scores: { vap: 0.52, clabsi: 0.38, cauti: 0.08, combined: 0.49 },
        vitals: { hr: 88, temp: 37.9, spo2: 97, rr: 18, bp: "124/78" },
        trend: "stable",
    },
    {
        id: "ICU-0334", age: 71, gender: "M", unit: "MICU", dayInICU: 9,
        devices: { vent: false, ventHours: 0, cvc: true, cvcHours: 216, cath: true, cathHours: 180 },
        scores: { vap: 0.11, clabsi: 0.82, cauti: 0.69, combined: 0.71 },
        vitals: { hr: 94, temp: 38.2, spo2: 98, rr: 16, bp: "132/82" },
        trend: "rising",
    },
    {
        id: "ICU-0567", age: 43, gender: "F", unit: "CCU", dayInICU: 2,
        devices: { vent: false, ventHours: 0, cvc: true, cvcHours: 48, cath: true, cathHours: 44 },
        scores: { vap: 0.09, clabsi: 0.27, cauti: 0.31, combined: 0.29 },
        vitals: { hr: 76, temp: 37.1, spo2: 99, rr: 14, bp: "128/80" },
        trend: "stable",
    },
    {
        id: "ICU-0789", age: 59, gender: "M", unit: "NSICU", dayInICU: 5,
        devices: { vent: true, ventHours: 108, cvc: false, cvcHours: 0, cath: true, cathHours: 100 },
        scores: { vap: 0.63, clabsi: 0.14, cauti: 0.55, combined: 0.58 },
        vitals: { hr: 91, temp: 38.0, spo2: 96, rr: 20, bp: "138/86" },
        trend: "rising",
    },
];

export const MOCK_ALERTS = [
    { id: "A001", patientId: "ICU-1042", type: "VAP", level: "RED", time: "4 min ago", score: 0.78, explanation: "FiO₂ elevated to 0.68, ventilator day 6, WBC trending up to 17.2K", acked: false },
    { id: "A002", patientId: "ICU-0334", type: "CLABSI", level: "RED", time: "11 min ago", score: 0.82, explanation: "CVC dwell 9 days, positive blood culture flagged, fever 38.2°C", acked: false },
    { id: "A003", patientId: "ICU-0789", type: "VAP", level: "AMBER", time: "28 min ago", score: 0.63, explanation: "PEEP increased, SpO₂ drift from 98 → 96%, ventilator day 5", acked: false },
    { id: "A004", patientId: "ICU-0334", type: "CAUTI", level: "AMBER", time: "1h ago", score: 0.69, explanation: "Catheter day 7.5, urine output declining, creatinine rising", acked: true },
    { id: "A005", patientId: "ICU-1042", type: "CLABSI", level: "AMBER", time: "2h ago", score: 0.61, explanation: "CVC day 5, WBC 14.8K, lactate mildly elevated", acked: true },
];

export const generateTrajectory = (baseScore, hours = 72) => {
    const points = [];
    let score = Math.max(0.1, baseScore - 0.35);
    for (let h = hours; h >= 0; h--) {
        score = Math.min(0.99, Math.max(0.05, score + (Math.random() - 0.38) * 0.04));
        if (h < 12) score = Math.min(0.99, score + 0.015);
        points.push({
            h: `-${h}h`,
            vap: +(score * 0.90 + Math.random() * 0.06).toFixed(2),
            clabsi: +(score * 0.75 + Math.random() * 0.08).toFixed(2),
            cauti: +(score * 0.60 + Math.random() * 0.07).toFixed(2),
        });
    }
    return points;
};

export const SHAP_DATA = {
    vap: [
        { label: "FiO₂ (Inspired Oxygen)", value: "0.68", shap: 0.18, dir: "up" },
        { label: "Ventilator Duration", value: "144 hrs", shap: 0.15, dir: "up" },
        { label: "Body Temperature", value: "38.6°C", shap: 0.09, dir: "up" },
        { label: "PEEP Level", value: "10 cmH₂O", shap: 0.07, dir: "up" },
        { label: "WBC Count", value: "17.2 K/uL", shap: 0.06, dir: "up" },
        { label: "SpO₂", value: "94%", shap: -0.04, dir: "down" },
    ],
    clabsi: [
        { label: "CVC Dwell Time", value: "5 days", shap: 0.16, dir: "up" },
        { label: "WBC Count", value: "17.2 K/uL", shap: 0.11, dir: "up" },
        { label: "Lactate", value: "2.1 mmol/L", shap: 0.08, dir: "up" },
        { label: "Body Temperature", value: "38.6°C", shap: 0.07, dir: "up" },
        { label: "Platelet Count", value: "148 K/uL", shap: -0.05, dir: "down" },
    ],
    cauti: [
        { label: "Catheter Duration", value: "96 hrs", shap: 0.12, dir: "up" },
        { label: "Urine Output", value: "↓ 28 mL/hr", shap: 0.10, dir: "up" },
        { label: "Creatinine", value: "1.8 mg/dL", shap: 0.07, dir: "up" },
        { label: "Body Temperature", value: "38.6°C", shap: 0.05, dir: "up" },
        { label: "WBC Count", value: "17.2 K/uL", shap: -0.03, dir: "down" },
    ],
};
