import React from 'react';

export function TypeGlyph({ type = 'essay', size = 22 }) {
  const t = String(type).toLowerCase();
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{ display: 'block', overflow: 'visible' }}>
      {t === 'essay' && <circle cx={12} cy={12} r={9} fill="none" stroke="var(--mark-stroke)" strokeWidth={1} />}
      {t === 'project' && (
        <>
          <circle cx={12} cy={12} r={9} fill="none" stroke="var(--mark-stroke)" strokeWidth={1} />
          <ellipse cx={12} cy={12} rx={11} ry={4.5} fill="none" stroke="var(--text-faint)" strokeWidth={0.9} />
          <circle cx={23} cy={12} r={1.6} fill="var(--mark-point)" />
        </>
      )}
      {t === 'dialogue' && (
        <>
          <circle cx={8.5} cy={12} r={7} fill="none" stroke="var(--mark-stroke)" strokeWidth={1} />
          <circle cx={15.5} cy={12} r={7} fill="none" stroke="var(--text-label)" strokeWidth={1} />
        </>
      )}
    </svg>
  );
}
