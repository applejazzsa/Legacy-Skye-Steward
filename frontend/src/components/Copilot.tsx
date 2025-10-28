import { useEffect, useState } from "react";
import { useAppStore, makeRange } from "../store";
import { api } from "../api";

export default function Copilot() {
  const { range } = useAppStore();
  const { date_from, date_to } = makeRange(range);
  const [text, setText] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      const res = await api.copilotSummary?.({ date_from, date_to });
      if (!alive) return;
      setText(res?.summary || "Copilot unavailable. Set OPENAI_API_KEY on backend for AI summaries.");
      setLoading(false);
    })();
    return () => {
      alive = false;
    };
  }, [date_from, date_to]);

  return (
    <div className="card">
      <h3>Steward Copilot</h3>
      {loading ? (
        <div className="skeleton" style={{height: 80}} />
      ) : (
        <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.45 }}>{text}</div>
      )}
    </div>
  );
}

