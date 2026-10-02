import * as React from 'react';

/** Marginalia role — italic Newsreader, no mono treatment. Use for a note or
 * concept you personally learned while researching, written in first person.
 * Never use for factual/dictionary-style definitions — that's MarginNote. */
export interface MarginThoughtProps {
  children?: React.ReactNode;
  style?: React.CSSProperties;
}
export declare function MarginThought(props: MarginThoughtProps): JSX.Element;
