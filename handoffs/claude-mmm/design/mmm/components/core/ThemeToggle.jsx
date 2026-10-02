import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

/** Switches [data-theme] between 'light' and 'dark' on the document root.
 * Reference implementation only — the Mecca Pact draft's toggle predates the
 * token-based dark palette in foundations/colors.css and should be reconciled
 * against this version rather than kept as its own one-off. */
export function ThemeToggle({ theme = 'light', onChange, style }) {
  const isDark = theme === 'dark';
  return (
    <button
      type="button"
      onClick={() => onChange && onChange(isDark ? 'light' : 'dark')}
      aria-label="Toggle dark mode"
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 'var(--space-1)',
        background: 'none', border: 'none', cursor: 'pointer', padding: 0,
        color: 'var(--text-label)',
        ...style
      }}>
      <MonoLabel size="sm">{isDark ? 'Light' : 'Dark'}</MonoLabel>
    </button>
  );
}
