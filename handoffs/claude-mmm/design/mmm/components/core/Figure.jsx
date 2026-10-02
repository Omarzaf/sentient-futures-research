import React from 'react';
import { MonoLabel } from './MonoLabel.jsx';

export function Figure({ src, alt = '', caption, height = 230 }) {
  return (
    <figure style={{ margin: 0 }}>
      <div style={{
        width: '100%', height, borderRadius: 'var(--radius-image)', overflow: 'hidden',
        background: 'var(--surface-hover)', border: '1px solid var(--rule-hairline)'
      }}>
        {src ? <img src={src} alt={alt} style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} /> : null}
      </div>
      {caption ? (
        <figcaption style={{ marginTop: 'var(--space-2)', lineHeight: 1.6 }}>
          <MonoLabel size="sm" tone="faint">{caption}</MonoLabel>
        </figcaption>
      ) : null}
    </figure>
  );
}
