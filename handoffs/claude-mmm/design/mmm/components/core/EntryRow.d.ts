import * as React from 'react';

/**
 * One line in the contents index: numeral, type glyph, title + excerpt, type and date.
 * @startingPoint section="Blog" subtitle="Contents index row" viewport="760x110"
 */
export interface EntryRowProps {
  /** Roman numeral, e.g. "IV". */
  numeral?: string;
  type?: 'essay' | 'project' | 'dialogue';
  title?: string;
  excerpt?: string;
  /** Uppercase short date, e.g. "AUG 2026". */
  date?: string;
  href?: string;
  showGlyph?: boolean;
}
export declare function EntryRow(props: EntryRowProps): JSX.Element;
