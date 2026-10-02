import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

/** Findings-list block placed directly after the hero, on research-substantial
 * entries only. Distinct from the lead paragraph (what it's about) and the
 * thesis line (the argument) — this is the compressed conclusions. */
export function TLDR({ items = [], style }) {
  if (!items.length) return null;
  return (
    <div style={{
      borderTop: '1px solid var(--rule-structural)',
      borderBottom: '1px solid var(--rule-structural)',
      padding: 'var(--gap-block) 0',
      margin: 'var(--gap-page) 0',
      ...style
    }}>
      <div style={{ marginBottom: 'var(--gap-heading-body)' }}>
        <MonoLabel size="lg">TL;DR</MonoLabel>
      </div>
      <ul style={{ margin: 0, paddingLeft: '1.1em' }}>
        {items.map((item, i) => (
          <li key={i} style={{
            fontFamily: 'var(--font-body)', fontSize: 'var(--type-body-size)',
            lineHeight: 'var(--type-body-line)', color: 'var(--text-body)',
            marginBottom: i < items.length - 1 ? 'var(--space-1)' : 0
          }}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
