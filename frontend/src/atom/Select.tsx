// feat(ui): accessible Select (combobox) with keyboard support
import React, { useEffect, useMemo, useRef, useState } from "react";

type Option<T extends string | number> = { label: string; value: T };

type SelectProps<T extends string | number> = {
  options: Option<T>[];
  value: T;
  onChange: (v: T) => void;
  label?: string;
  id?: string;
};

export default function Select<T extends string | number>({ options, value, onChange, label, id }: SelectProps<T>) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<number>(() => Math.max(0, options.findIndex(o => o.value === value)));
  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const selected = useMemo(() => options.find(o => o.value === value) || options[0], [options, value]);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!rootRef.current) return;
      if (!rootRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  function onKey(e: React.KeyboardEvent) {
    if (!open) {
      if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
        setOpen(true);
        e.preventDefault();
      }
      return;
    }
    if (e.key === "Escape") { setOpen(false); return; }
    if (e.key === "ArrowDown") { setActive((i) => Math.min(options.length - 1, i + 1)); e.preventDefault(); }
    if (e.key === "ArrowUp") { setActive((i) => Math.max(0, i - 1)); e.preventDefault(); }
    if (e.key === "Enter") { const opt = options[active]; if (opt) onChange(opt.value); setOpen(false); e.preventDefault(); }
  }

  useEffect(() => {
    if (!open) return;
    const el = listRef.current?.children[active] as HTMLElement | undefined;
    el?.scrollIntoView({ block: "nearest" });
  }, [open, active]);

  return (
    <div ref={rootRef} className="field" style={{ position: "relative" }}>
      {label && <label htmlFor={id}>{label}</label>}
      <button
        id={id}
        role="combobox"
        aria-expanded={open}
        aria-controls={id ? `${id}-listbox` : undefined}
        onClick={() => setOpen((o) => !o)}
        onKeyDown={onKey}
        style={{ width: "100%", textAlign: "left" }}
      >
        {selected?.label}
      </button>
      {open && (
        <ul
          id={id ? `${id}-listbox` : undefined}
          role="listbox"
          ref={listRef}
          style={{
            position: "absolute",
            zIndex: 1000,
            inset: "auto 0 0 0",
            transform: "translateY(100%)",
            background: "var(--panel)",
            border: "1px solid var(--line)",
            borderRadius: 10,
            maxHeight: 220,
            overflow: "auto",
            padding: 6,
            margin: 0,
            listStyle: "none",
          }}
        >
          {options.map((opt, i) => (
            <li
              key={String(opt.value)}
              role="option"
              aria-selected={opt.value === value}
              onMouseEnter={() => setActive(i)}
              onClick={() => { onChange(opt.value); setOpen(false); }}
              style={{
                padding: "6px 8px",
                borderRadius: 8,
                cursor: "pointer",
                background: i === active ? "#1a2543" : "transparent",
              }}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

