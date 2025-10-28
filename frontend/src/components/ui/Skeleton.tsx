import React from "react";

type BaseProps = { className?: string; style?: React.CSSProperties };

export function Skeleton({ className = "", style }: BaseProps) {
  return <div className={`skeleton ${className}`.trim()} style={style} />;
}

export function SkeletonTitle(props: BaseProps) {
  return <Skeleton style={{ height: 16, width: "40%", ...props.style }} className={props.className} />;
}

export function SkeletonLine(props: BaseProps) {
  return <Skeleton style={{ height: 14, width: "100%", ...props.style }} className={props.className} />;
}

export function SkeletonCard({ lines = 3, style }: { lines?: number; style?: React.CSSProperties }) {
  return (
    <div className="card" aria-busy="true" aria-live="polite">
      <SkeletonTitle />
      <div style={{ display: "grid", gap: 8, marginTop: 8 }}>
        {Array.from({ length: lines }).map((_, i) => (
          <SkeletonLine key={i} />
        ))}
      </div>
    </div>
  );
}

export default Skeleton;

