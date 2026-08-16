import type { Theme } from 'vitepress';
import DefaultTheme from 'vitepress/theme';
import { setupSmoothScroll } from '../plugins/smoothScroll';
import TerminalOutput from './components/TerminalOutput.vue';
// @ts-ignore-next-line
import './style.css';

export default {
  enhanceApp({ app }) {
    app.component('TerminalOutput', TerminalOutput);
  },
  extends: DefaultTheme,
  setup() {
    setupSmoothScroll();
  },
} satisfies Theme;
