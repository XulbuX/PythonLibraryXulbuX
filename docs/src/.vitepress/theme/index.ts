import type { Theme } from 'vitepress';
import DefaultTheme from 'vitepress/theme';
import { setupSmoothScroll } from '../plugins/smoothScroll';
import TerminalOutput from './components/TerminalOutput.vue';
import AttachedCode from './components/AttachedCode.vue';
// @ts-ignore-next-line
import './style.css';

export default {
  enhanceApp({ app }) {
    app.component('TerminalOutput', TerminalOutput);
    app.component('AttachedCode', AttachedCode);
  },
  extends: DefaultTheme,
  setup() {
    setupSmoothScroll();
  },
} satisfies Theme;
