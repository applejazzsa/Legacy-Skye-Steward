// frontend/src/components/CommandPalette.tsx
import React, { useEffect, useRef, useState } from "react";

type Command = {
  id: string;
  title: string;
  onRun: () => void;
};

const DEFAULT_CMDS: Command[] = [
  { id: "reload", title: "Reload data", onRun: () => window.location.reload() },
];

declare global {
  interface Window {
    openCommandPalette?: () => void;
  }
}

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = DEFAULT_CMDS.filter((c) => c.title.toLowerCase().includes(q.toLowerCase()));

  // expose open on window
  useEffect(() => {
    window.openCommandPalette = () => setOpen(true);
    return () => {
      window.openCommandPalette = undefined;
    };
  }, []);

  // keyboard shortcuts: '/' and Cmd/Ctrl+K
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const isModK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
      const isSlash = !e.ctrlKey && !e.metaKey && e.key === "/";
      if (isModK || isSlash) {
        e.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 0);
  }, [open]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      onClick={() => setOpen(false)}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,.45)",
        backdropFilter: "blur(2px)",
        zIndex: 999,
        display: "grid",
        placeItems: "start center",
        paddingTop: "15vh",
      }}
    >
      <div
        className="card"
        onClick={(e) => e.stopPropagation()}
        style={{ width: 560, maxWidth: "92vw" }}
      >
        <input
          ref={inputRef}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Type a command…"
          style={{
            width: "100%",
            padding: "12px 14px",
            borderRadius: 10,
            background: "rgba(255,255,255,.06)",
            border: "1px solid rgba(255,255,255,.08)",
            color: "inherit",
          }}
        />
        <div style={{ marginTop: 10, maxHeight: 240, overflow: "auto" }}>
          {filtered.length === 0 ? (
            <div className="muted">No commands.</div>
          ) : (
            filtered.map((c) => (
              <button
                key={c.id}
                className="btn"
                style={{ width: "100%", textAlign: "left", marginBottom: 6 }}
                onClick={() => {
                  setOpen(false);
                  setTimeout(c.onRun, 0);
                }}
              >
                {c.title}
              </button>
            ))
          )}
        </div>
        <div className="muted" style={{ marginTop: 8 }}>
          Shortcuts: <kbd>/</kbd> or <kbd>⌘/Ctrl</kbd>+<kbd>K</kbd>
        </div>
      </div>
    </div>
  );
}
