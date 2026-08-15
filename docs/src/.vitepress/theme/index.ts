import type { Theme } from 'vitepress';
import DefaultTheme from 'vitepress/theme';
import TerminalOutput from './TerminalOutput.vue';
// @ts-ignore-next-line
import './style.css';

export default {
  enhanceApp({ app }) {
    app.component('TerminalOutput', TerminalOutput);
  },
  extends: DefaultTheme,
} satisfies Theme;
