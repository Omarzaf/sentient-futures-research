import * as React from 'react';

export interface LeftNavSection {
  id: string;
  num: string;   // e.g. "01"
  title: string;
}

/** Sticky left-rail table of contents. Returns null (renders nothing) when
 * `sections` is empty — callers should not render a LeftNav wrapper at all
 * for short entries; this guard exists so that omission is safe by default. */
export interface LeftNavProps {
  sections: LeftNavSection[];
  activeId?: string;
  style?: React.CSSProperties;
}
export declare function LeftNav(props: LeftNavProps): JSX.Element | null;
