import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

export function MetaList({ items = [] }) {
  return (
    <dl style={{
      margin: 0, paddingTop: 'var(--space-3)', borderTop: '1px solid var(--rule-hairline)',
      lineHeight: 2
    }}>
      {items.map((it, i) => (
        <div key={i}>
          <MonoLabel size="sm">{it.label} — {it.value}</MonoLabel>
        </div>
      ))}
    </dl>
  );
}
