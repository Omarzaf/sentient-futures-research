import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

/** Numbered source list at the bottom of an entry. Citations in the body
 * link down here via superscript markers; this is the only place sources
 * live now — the right rail no longer carries a static source list. */
export function Endnotes({ items = [], style }) {
  if (!items.length) return null;
  return (
    <div style={{ borderTop: '1px solid var(--rule-structural)', paddingTop: 'var(--gap-block)', marginTop: 'var(--gap-section)', ...style }}>
      <div style={{ marginBottom: 'var(--gap-heading-body)' }}>
        <MonoLabel size="lg">Sources</MonoLabel>
      </div>
      <ol style={{ margin: 0, paddingLeft: '1.4em', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {items.map((item) => (
          <li key={item.id} id={`note-${item.id}`} style={{
            fontFamily: 'var(--font-body)', fontSize: 'var(--type-support-size)',
            lineHeight: 'var(--type-support-line)', color: 'var(--text-support)'
          }}>
            <a href={item.href} target="_blank" rel="noreferrer" style={{ color: 'inherit' }}>{item.label}</a>
            {item.detail ? <span> — {item.detail}</span> : null}
          </li>
        ))}
      </ol>
    </div>
  );
}

/** Inline superscript marker in the body that jumps to a numbered endnote. */
export function Citation({ id, n }) {
  return (
    <sup>
      <a href={`#note-${id}`} style={{ color: 'var(--copper)', textDecoration: 'none' }}>{n}</a>
    </sup>
  );
}
