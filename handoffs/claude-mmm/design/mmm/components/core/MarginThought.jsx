import React from 'react';

/** A personal note in the right rail — written in Umar's own voice, first person,
 * as if jotted in the margin while researching. This is the one place in the
 * system meant to read as unmistakably human, not systematized. */
export function MarginThought({ children, style }) {
  return (
    <p style={{
      fontFamily: 'var(--font-body)',
      fontStyle: 'var(--type-marginalia-style)',
      fontWeight: 'var(--type-marginalia-weight)',
      fontSize: 'var(--type-marginalia-size)',
      lineHeight: 'var(--type-marginalia-line)',
      maxWidth: 'var(--measure-marginalia)',
      color: 'var(--text-lead)',
      margin: 0,
      ...style
    }}>{children}</p>
  );
}
