import * as React from 'react';

export interface ThemeToggleProps {
  theme?: 'light' | 'dark';
  onChange?: (next: 'light' | 'dark') => void;
  style?: React.CSSProperties;
}
export declare function ThemeToggle(props: ThemeToggleProps): JSX.Element;
