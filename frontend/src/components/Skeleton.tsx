// frontend/src/components/Skeleton.tsx
import React, { useEffect } from "react";

/**
 * Zero-dependency skeleton with a tiny injected stylesheet.
 * Use <SkeletonBlock /> to draw grey shimmering blocks.
 */

let injected = false;
function injectCSS() {
  if (injected) return;
  injected = true;
  const css = `
  @keyframes skPulse { 0%{opacity:.45} 50%{opacity:.9} 100%{opacity:.45} }
  .sk { background: rgba(255,255,255,.08); border-radius: 8px; animation: skPulse 1.4s ease-in-out infinite; }
  `;
  const tag = document.createElement("style");
  tag.setAttribute("data-skeleton", "1");
  tag.textContent = css;
  document.head.appendChild(tag);
}

export function SkeletonBlock({
  width = "100%",
  height = 12,
  radius = 8,
  style,
}: {
  width?: number | string;
  height?: number | string;
  radius?: number;
  style?: React.CSSProperties;
}) {
  useEffect(injectCSS, []);
  return <div className="sk" style={{ width, height, borderRadius: radius, ...style }} />;
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  useEffect(injectCSS, []);
  return (
    <div>
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBlock key={i} height={12} style={{ marginBottom: 10 }} />
      ))}
    </div>
  );
}
