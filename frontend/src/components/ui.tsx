import { PropsWithChildren } from "react";

export function Card({ children }: PropsWithChildren) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 shadow-lg shadow-black/20">
      {children}
    </div>
  );
}

export function Stat({
  label,
  value,
  sub,
  progress, // 0..100 optional
}: {
  label: string;
  value: string;
  sub?: string;
  progress?: number;
}) {
  const pct = Math.max(0, Math.min(100, progress ?? -1));
  return (
    <Card>
      <div className="text-sm text-white/60">{label}</div>
      <div className="mt-2 text-3xl font-semibold tracking-tight">{value}</div>
      {sub ? <div className="mt-1 text-xs text-white/50">{sub}</div> : null}
      {pct >= 0 ? (
        <div className="mt-3">
          <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
            <div
              className="h-full rounded-full bg-white/30"
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="mt-1 text-right text-[11px] text-white/50">{pct}%</div>
        </div>
      ) : null}
    </Card>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl bg-white/5 ${className}`} />;
}

export function Empty({ title, note }: { title: string; note?: string }) {
  return (
    <div className="flex h-40 items-center justify-center text-center">
      <div>
        <div className="text-white/70">{title}</div>
        {note && <div className="mt-1 text-xs text-white/50">{note}</div>}
      </div>
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
      {message}
    </div>
  );
}

export function Button(
  props: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "ghost" }
) {
  const { className = "", variant = "default", ...rest } = props;
  const base =
    variant === "ghost"
      ? "hover:bg-white/5"
      : "bg-white/10 hover:bg-white/20 border border-white/10";
  return (
    <button
      {...rest}
      className={`rounded-lg px-3 py-2 text-sm transition-colors ${base} ${className}`}
    />
  );
}
