import React from 'react';

export function MonoLabel({ children, size = 'md', tone = 'label', style }) {
  const sizes = {
    sm: { fontSize: 'var(--type-label-size-sm)', letterSpacing: 'var(--type-label-track-sm)' },
    md: { fontSize: 'var(--type-label-size)', letterSpacing: 'var(--type-label-track)' },
    lg: { fontSize: 'var(--type-label-size)', letterSpacing: 'var(--type-label-track-lg)' }
  };
  const tones = { label: 'var(--text-label)', faint: 'var(--text-faint)', ink: 'var(--text-display)' };
  return (
    <span style={{
      fontFamily: 'var(--font-mono)',
      textTransform: 'uppercase',
      color: tones[tone] || tones.label,
      ...sizes[size] || sizes.md,
      ...style
    }}>{children}</span>
  );
}
