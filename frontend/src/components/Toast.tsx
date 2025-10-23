// src/components/Toast.tsx
import { useEffect } from "react";

export type Toast = { id: string; kind: "success" | "error" | "info"; msg: string };

type Props = {
  toasts: Toast[];
  onDismiss: (id: string) => void;
  durationMs?: number;
};

export default function Toasts({ toasts, onDismiss, durationMs = 3500 }: Props) {
  useEffect(() => {
    const timers = toasts.map((t) =>
      setTimeout(() => onDismiss(t.id), durationMs)
    );
    return () => timers.forEach(clearTimeout);
  }, [toasts, onDismiss, durationMs]);

  return (
    <div className="fixed right-4 bottom-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={[
            "rounded-lg border px-3 py-2 text-sm shadow",
            t.kind === "success"
              ? "bg-green-50 border-green-200 text-green-900"
              : t.kind === "error"
              ? "bg-red-50 border-red-200 text-red-900"
              : "bg-slate-50 border-slate-200 text-slate-900",
          ].join(" ")}
        >
          {t.msg}
        </div>
      ))}
    </div>
  );
}
