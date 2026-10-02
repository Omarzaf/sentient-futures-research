import * as React from 'react';

/**
 * The series identity mark: a pulsar-map ring diagram with a rotating outer tick ring
 * and one copper point. Use once per view, never repeated or recolored.
 * @startingPoint section="Brand" subtitle="Series identity mark" viewport="700x200"
 */
export interface SeriesMarkProps {
  /** Rendered width and height in px. Default 132. */
  size?: number;
  /** Animate the outer tick ring (180s rotation). Default true. */
  rotate?: boolean;
  style?: React.CSSProperties;
}
export declare function SeriesMark(props: SeriesMarkProps): JSX.Element;
