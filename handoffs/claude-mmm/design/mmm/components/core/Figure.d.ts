import * as React from 'react';

/** An image in the right rail of an entry, with a numbered mono caption ("FIG. 01 — …"). Images stay small; they support the text, never lead it. */
export interface FigureProps {
  src?: string;
  alt?: string;
  /** Mono caption, conventionally "FIG. 0N — DESCRIPTION". */
  caption?: string;
  /** Height in px. Default 230; never exceed 320 in the rail. */
  height?: number;
}
export declare function Figure(props: FigureProps): JSX.Element;
