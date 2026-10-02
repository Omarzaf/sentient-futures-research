import React from 'react';

export function DashedRule({ style }) {
  return <div style={{
    flex: 1, height: 1,
    background: 'repeating-linear-gradient(90deg, var(--text-faint) 0, var(--text-faint) 3px, transparent 3px, transparent 9px)',
    ...style
  }} />;
}
