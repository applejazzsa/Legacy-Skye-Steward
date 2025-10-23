// src/components/Sparkline.tsx
type Props = {
  points: number[]; // y-values
  width?: number;
  height?: number;
};

export default function Sparkline({ points, width = 560, height = 120 }: Props) {
  if (!points.length) {
    return <div className="text-xs text-gray-500">No data</div>;
  }
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const stepX = width / Math.max(1, points.length - 1);

  const path = points
    .map((v, i) => {
      const x = i * stepX;
      const y = height - ((v - min) / range) * height;
      return `${i === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");

  const last = points[points.length - 1];

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-28">
      <path d={path} fill="none" stroke="currentColor" strokeWidth="2" />
      <text
        x={width - 8}
        y={16}
        textAnchor="end"
        fontSize="12"
        fill="currentColor"
      >
        Latest: {last.toFixed(2)}
      </text>
    </svg>
  );
}
