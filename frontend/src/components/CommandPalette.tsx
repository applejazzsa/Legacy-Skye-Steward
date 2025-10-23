// src/components/CommandPalette.tsx
import { useMemo, useState } from "react";

export type Command = {
  id: string;
  label: string;
  hint?: string;
  run: () => void;
};

export default function CommandPalette({
  open,
  onClose,
  commands,
}: {
  open: boolean;
  onClose: () => void;
  commands: Command[];
}) {
  const [q, setQ] = useState("");

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return commands;
    return commands.filter((c) => c.label.toLowerCase().includes(s));
  }, [q, commands]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative z-50 max-w-xl mx-auto mt-24 bg-white rounded-xl border shadow">
        <input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Type a command…"
          className="w-full px-3 py-2 border-b rounded-t-xl outline-none"
        />
        <ul className="max-h-72 overflow-auto">
          {filtered.map((c) => (
            <li
              key={c.id}
              className="px-3 py-2 cursor-pointer hover:bg-gray-50 flex justify-between"
              onClick={() => {
                c.run();
                onClose();
              }}
            >
              <span>{c.label}</span>
              {c.hint && <span className="text-xs text-gray-500">{c.hint}</span>}
            </li>
          ))}
          {!filtered.length && (
            <li className="px-3 py-6 text-sm text-gray-500">No matches</li>
          )}
        </ul>
      </div>
    </div>
  );
}
