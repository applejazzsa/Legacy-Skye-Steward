import { useEffect, useState } from "react";
import { api } from "../api";
import { useAppStore } from "../store";

type Template = { id: number; name: string; schema?: any };

export default function Checklists() {
  const { tenant } = useAppStore();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [name, setName] = useState("Daily Open/Close");
  const [schemaText, setSchemaText] = useState('{"fields":[{"type":"boolean","id":"ready","label":"Open/Close checks done"}]}');
  const [resp, setResp] = useState<any | null>(null);

  async function refresh() {
    const rows = await api.listChecklistTemplates?.();
    setTemplates(Array.isArray(rows) ? rows : []);
  }
  useEffect(() => { refresh(); }, []);

  async function createTemplate() {
    try {
      const schema = JSON.parse(schemaText);
      await api.createChecklistTemplate?.({ name, schema });
      setName("");
      await refresh();
    } catch {
      alert("Invalid JSON schema");
    }
  }

  async function submitQuick(template_id: number) {
    const out = await api.submitChecklistResponse?.({ template_id, answers: { ready: true }, filled_by: "Demo" });
    setResp(out || { ok: false });
  }

  return (
    <div className="row two">
      <div className="card">
        <h3>Templates</h3>
        <div className="muted">Create or pick a checklist template.</div>
        <div style={{display:"grid", gap:8, marginTop:8}}>
          <input value={name} onChange={e=>setName(e.target.value)} placeholder="Template name" />
          <textarea rows={6} value={schemaText} onChange={e=>setSchemaText(e.target.value)} />
          <div>
            <button className="primary" onClick={createTemplate}>Save Template</button>
          </div>
        </div>
        <div style={{marginTop:10}}>
          <h4>Existing</h4>
          <ul>
            {templates.map(t => (
              <li key={t.id} style={{display:"flex",justifyContent:"space-between", gap:8, padding:"6px 0", borderBottom:"1px solid var(--line)"}}>
                <span>{t.name}</span>
                <button onClick={()=>submitQuick(t.id)}>Quick Submit</button>
              </li>
            ))}
            {!templates.length && <li className="muted">No templates yet.</li>}
          </ul>
        </div>
      </div>
      <div className="card">
        <h3>Last Submission</h3>
        {!resp && <div className="muted">Submit a quick response to preview payload.</div>}
        {resp && <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(resp, null, 2)}</pre>}
      </div>
    </div>
  );
}

