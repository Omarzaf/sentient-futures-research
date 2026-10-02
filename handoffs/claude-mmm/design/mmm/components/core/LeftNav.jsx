import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

/** Sticky contents nav for the left rail. Only render this component at all
 * if the entry has enough sections to warrant jumping between them — see
 * readme.md, "Entry template: the three-zone frame". */
export function LeftNav({ sections = [], activeId, style }) {
  if (!sections.length) return null;
  return (
    <nav style={{
      position: 'sticky', top: 'var(--space-6)',
      width: 'var(--rail-left-width)',
      display: 'flex', flexDirection: 'column', gap: 'var(--space-2)',
      ...style
    }}>
      <MonoLabel size="sm" tone="faint">Contents</MonoLabel>
      {sections.map((s) => (
        <a key={s.id} href={`#${s.id}`}
          style={{
            display: 'flex', gap: 'var(--space-2)', alignItems: 'baseline',
            textDecoration: 'none',
            color: s.id === activeId ? 'var(--text-display)' : 'var(--text-support)',
            transition: 'color var(--dur-hover) var(--ease-standard)'
          }}>
          <MonoLabel size="sm" tone={s.id === activeId ? 'ink' : 'faint'}>{s.num}</MonoLabel>
          <span style={{ fontFamily: 'var(--font-body)', fontSize: 14, lineHeight: 1.4 }}>{s.title}</span>
        </a>
      ))}
    </nav>
  );
}
