import * as React from 'react';

/** Build metadata under a rail figure: what it was made with, how long it took, where it ended up. */
export interface MetaListProps {
  items?: Array<{ label: string; value: string }>;
}
export declare function MetaList(props: MetaListProps): JSX.Element;
