import type { Theme } from 'vitepress';
import DefaultTheme from 'vitepress/theme';
import { setupCodeCopyBehavior } from '../plugins/codeCopyBehavior';
import { setupCodeScrollButtons } from '../plugins/codeScrollButtons';
import { setupSmoothScroll } from '../plugins/smoothScroll';
import AttachedCode from './components/AttachedCode.vue';
import TerminalOutput from './components/TerminalOutput.vue';
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
    setupCodeScrollButtons();
    setupCodeCopyBehavior();
  },
} satisfies Theme;
