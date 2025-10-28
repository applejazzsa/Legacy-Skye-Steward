import { useEffect, useState } from "react";
import { api } from "../api";

type Therapist = { id: number; name: string };
type Treatment = { id: number; name: string; duration_min?: number };
type Visit = { id: number; when_ts?: string; guest_name?: string; therapist_id?: number; treatment_id?: number; upgrade?: string; occasion?: string; feedback?: string; amount?: number };

export default function Spa() {
  const [therapists, setTherapists] = useState<Therapist[]>([]);
  const [treatments, setTreatments] = useState<Treatment[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [guest, setGuest] = useState("");
  const [therapistId, setTherapistId] = useState<number | undefined>(undefined);
  const [treatmentId, setTreatmentId] = useState<number | undefined>(undefined);
  const [upgrade, setUpgrade] = useState("");
  const [occasion, setOccasion] = useState("");
  const [feedback, setFeedback] = useState("");
  const [amount, setAmount] = useState<string>("");

  async function refresh() {
    const [ths, trs, v] = await Promise.all([
      api.listTherapists(),
      api.listTreatments(),
      api.listVisits(),
    ]);
    setTherapists(Array.isArray(ths) ? ths : []);
    setTreatments(Array.isArray(trs) ? trs : []);
    setVisits(Array.isArray(v) ? v : []);
    if (ths && ths.length) setTherapistId(ths[0].id);
    if (trs && trs.length) setTreatmentId(trs[0].id);
  }
  useEffect(() => { refresh(); }, []);

  async function addVisit() {
    const amt = Number(amount || 0);
    await api.createVisit({ guest_name: guest || undefined, therapist_id: therapistId, treatment_id: treatmentId, upgrade: upgrade || undefined, occasion: occasion || undefined, feedback: feedback || undefined, amount: Number.isFinite(amt) ? amt : 0 });
    setGuest(""); setUpgrade(""); setOccasion(""); setFeedback("");
    setAmount("");
    await refresh();
  }

  async function seedDefaults() {
    if (!therapists.length) {
      await api.createTherapist({ name: "Thandi" });
      await api.createTherapist({ name: "Kabelo" });
    }
    if (!treatments.length) {
      await api.createTreatment({ name: "Swedish Massage", duration_min: 60 });
      await api.createTreatment({ name: "Hot Stone", duration_min: 90 });
    }
    await refresh();
  }

  return (
    <div className="row two">
      <div className="card">
        <h3>Log Spa Visit</h3>
        <div className="muted">Treatments, therapists, upgrades, occasions, and feedback.</div>
        <div style={{display:"grid", gap:8, marginTop:8}}>
          <input placeholder="Guest name" value={guest} onChange={e=>setGuest(e.target.value)} />
          <div style={{display:"flex", gap:8}}>
            <select value={therapistId} onChange={e=>setTherapistId(Number(e.target.value))}>
              {therapists.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
            <select value={treatmentId} onChange={e=>setTreatmentId(Number(e.target.value))}>
              {treatments.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <input placeholder="Upgrade (optional)" value={upgrade} onChange={e=>setUpgrade(e.target.value)} />
          <input placeholder="Occasion (e.g. Birthday)" value={occasion} onChange={e=>setOccasion(e.target.value)} />
          <input placeholder="Amount (ZAR)" value={amount} onChange={e=>setAmount(e.target.value)} />
          <textarea rows={3} placeholder="Feedback (optional)" value={feedback} onChange={e=>setFeedback(e.target.value)} />
          <div style={{display:"flex", gap:8}}>
            <button className="primary" onClick={addVisit}>Save Visit</button>
            <button onClick={seedDefaults}>Seed Defaults</button>
          </div>
        </div>
      </div>
      <div className="card">
        <h3>Recent Visits</h3>
        <table className="table">
          <thead><tr><th>When</th><th>Guest</th><th>Therapist</th><th>Treatment</th><th>Upgrade</th><th>Occasion</th><th>Amount</th></tr></thead>
          <tbody>
            {visits.map(v => (
              <tr key={v.id}>
                <td>{v.when_ts ? new Date(v.when_ts).toLocaleString() : ""}</td>
                <td>{v.guest_name}</td>
                <td>{v.therapist_id}</td>
                <td>{v.treatment_id}</td>
                <td>{v.upgrade}</td>
                <td>{v.occasion}</td>
                <td>{Number(v.amount||0).toFixed(2)}</td>
              </tr>
            ))}
            {!visits.length && <tr><td className="muted" colSpan={7}>No visits yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
