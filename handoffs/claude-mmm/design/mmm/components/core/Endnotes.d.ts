import * as React from 'react';

export interface EndnoteItem {
  id: string;
  href: string;    // required — every citation must link to its primary source
  label: React.ReactNode;
  detail?: React.ReactNode;
}

export interface EndnotesProps {
  items: EndnoteItem[];
  style?: React.CSSProperties;
}
export declare function Endnotes(props: EndnotesProps): JSX.Element | null;

export interface CitationProps {
  /** Matches an EndnoteItem.id */
  id: string;
  /** The visible number, e.g. 1 */
  n: number | string;
}
export declare function Citation(props: CitationProps): JSX.Element;
