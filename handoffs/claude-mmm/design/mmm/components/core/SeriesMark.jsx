import React from 'react';

export function SeriesMark({ size = 132, rotate = true, style }) {
  const cx = 70, cy = 70;
  const ticks = Array.from({ length: 24 }, (_, i) => {
    const a = (i / 24) * Math.PI * 2;
    const inner = i % 6 === 0 ? 53 : 58;
    return {
      x1: cx + inner * Math.cos(a), y1: cy + inner * Math.sin(a),
      x2: cx + 64 * Math.cos(a), y2: cy + 64 * Math.sin(a)
    };
  });
  return (
    <svg width={size} height={size} viewBox="0 0 140 140" style={{ overflow: 'visible', ...style }}>
      <g style={rotate ? { animation: 'mmm-spin var(--dur-mark-rotation) linear infinite', transformBox: 'fill-box', transformOrigin: 'center' } : undefined}>
        <circle cx={cx} cy={cy} r={64} fill="none" stroke="var(--rule-structural)" strokeWidth={0.75} />
        {ticks.map((t, i) => (
          <line key={i} x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} stroke="var(--text-label)" strokeWidth={0.75} />
        ))}
      </g>
      <circle cx={cx} cy={cy} r={46} fill="none" stroke="var(--text-label)" strokeWidth={0.75} />
      <circle cx={cx} cy={cy} r={29} fill="none" stroke="var(--mark-stroke)" strokeWidth={1} />
      <ellipse cx={cx} cy={cy} rx={46} ry={17} fill="none" stroke="var(--text-faint)" strokeWidth={0.75} />
      <circle cx={cx} cy={cy} r={6} fill="none" stroke="var(--text-display)" strokeWidth={1.2} />
      <circle cx={116} cy={70} r={2.6} fill="var(--mark-point)" />
      <circle cx={70} cy={41} r={1.8} fill="var(--text-display)" />
    </svg>
  );
}
