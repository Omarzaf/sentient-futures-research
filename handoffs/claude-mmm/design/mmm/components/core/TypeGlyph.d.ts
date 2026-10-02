import * as React from 'react';

/** Astronomical glyph identifying an entry's type. Essay = single ring, Project = ring with orbiting body, Dialogue = two intersecting orbits. */
export interface TypeGlyphProps {
  type?: 'essay' | 'project' | 'dialogue';
  /** Box size in px. Default 22. */
  size?: number;
}
export declare function TypeGlyph(props: TypeGlyphProps): JSX.Element;
