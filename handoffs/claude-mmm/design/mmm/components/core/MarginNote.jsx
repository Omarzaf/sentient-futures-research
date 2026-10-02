import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

/** A factual, dictionary-style explanation in the right rail — defines a
 * concept or term encountered during research. Impersonal and functional,
 * the opposite register of MarginThought. */
export function MarginNote({ term, children, style }) {
  return (
    <div style={{ ...style }}>
      {term ? (
        <div style={{ marginBottom: 'var(--space-1)' }}>
          <MonoLabel size="sm">{term}</MonoLabel>
        </div>
      ) : null}
      <p style={{
        fontFamily: 'var(--font-body)',
        fontSize: 'var(--type-support-size)',
        lineHeight: 'var(--type-support-line)',
        color: 'var(--text-support)',
        margin: 0
      }}>{children}</p>
    </div>
  );
}
