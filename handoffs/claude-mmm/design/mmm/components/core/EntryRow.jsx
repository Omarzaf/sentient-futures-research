import React from 'react';
import { TypeGlyph } from './TypeGlyph.jsx';
import { MonoLabel } from './MonoLabel.jsx';

export function EntryRow({ numeral, type = 'essay', title, excerpt, date, href = '#', showGlyph = true }) {
  const [hover, setHover] = React.useState(false);
  return (
    <a href={href}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        display: 'grid', gridTemplateColumns: '44px 26px 1fr auto', gap: 'var(--space-3)',
        alignItems: 'center', textDecoration: 'none', color: 'inherit',
        padding: 'var(--row-pad-y) var(--space-2) var(--row-pad-y) 4px',
        paddingLeft: hover ? 'var(--space-2)' : '4px',
        background: hover ? 'var(--surface-hover)' : 'transparent',
        borderBottom: '1px solid var(--rule-hairline)',
        transition: 'background var(--dur-hover) var(--ease-standard), padding var(--dur-hover) var(--ease-standard)'
      }}>
      <MonoLabel size="sm" tone="faint">{numeral}</MonoLabel>
      <span>{showGlyph ? <TypeGlyph type={type} /> : null}</span>
      <span>
        <span style={{ display: 'block', fontFamily: 'var(--font-display)', fontSize: 'var(--type-listing-size)', lineHeight: 'var(--type-listing-line)', marginBottom: 'var(--space-1)' }}>{title}</span>
        <span style={{ display: 'block', fontFamily: 'var(--font-body)', fontSize: 'var(--type-support-size)', lineHeight: 'var(--type-support-line)', color: 'var(--text-support)' }}>{excerpt}</span>
      </span>
      <span style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
        <MonoLabel size="sm">{type}</MonoLabel>
        <span style={{ display: 'block', marginTop: 6 }}><MonoLabel size="sm" tone="faint">{date}</MonoLabel></span>
      </span>
    </a>
  );
}
