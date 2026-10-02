import * as React from 'react';

/** Renders null when `items` is empty — omit the TL;DR entirely for entries
 * without compressible findings rather than passing an empty array to force
 * a hidden block. */
export interface TLDRProps {
  items: React.ReactNode[];
  style?: React.CSSProperties;
}
export declare function TLDR(props: TLDRProps): JSX.Element | null;
