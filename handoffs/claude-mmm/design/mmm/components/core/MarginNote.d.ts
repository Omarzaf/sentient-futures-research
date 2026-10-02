import * as React from 'react';

/** Explanation role for the right rail — a term paired with a factual
 * definition, in the standard mono-label + body treatment. Not written in
 * first person; that's MarginThought. */
export interface MarginNoteProps {
  term?: React.ReactNode;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}
export declare function MarginNote(props: MarginNoteProps): JSX.Element;
