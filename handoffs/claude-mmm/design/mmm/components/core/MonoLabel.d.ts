import * as React from 'react';

/** Uppercase tracked-out mono label — the system's only non-serif text. Dates, types, metadata, section markers. */
export interface MonoLabelProps {
  children?: React.ReactNode;
  /** sm = 10px/0.1em, md = 11px/0.14em, lg = 11px/0.18em. Default md. */
  size?: 'sm' | 'md' | 'lg';
  tone?: 'label' | 'faint' | 'ink';
  style?: React.CSSProperties;
}
export declare function MonoLabel(props: MonoLabelProps): JSX.Element;
