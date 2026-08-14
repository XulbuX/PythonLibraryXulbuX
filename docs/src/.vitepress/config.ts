import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { type ThemeOptions, defineConfig } from 'vitepress';

const dirname = path.dirname(fileURLToPath(import.meta.url)),
  sidebar = JSON.parse(fs.readFileSync(path.resolve(dirname, 'sidebar.json'), 'utf8')),
  customTheme: ThemeOptions = {
    colors: {
      'editor.background': 'var(--shiki-color-background)',
      'editor.foreground': 'var(--shiki-color-text)',
    },
    name: 'css-variables',
    tokenColors: [
      {
        scope: ['keyword', 'storage', 'variable.language', 'entity.name.type'],
        settings: { foreground: 'var(--shiki-token-keyword)' },
      },
      { scope: ['string'], settings: { foreground: 'var(--shiki-token-string)' } },
      {
        scope: ['comment', 'punctuation.definition.comment'],
        settings: { fontStyle: 'italic', foreground: 'var(--shiki-token-comment)' },
      },
      {
        scope: ['constant', 'variable.other.constant', 'support.constant'],
        settings: { foreground: 'var(--shiki-token-constant)' },
      },
      {
        scope: ['entity.name.function', 'support.function', 'meta.function-call'],
        settings: { foreground: 'var(--shiki-token-function)' },
      },
      {
        scope: ['variable.parameter', 'entity.name.variable.parameter'],
        settings: { foreground: 'var(--shiki-token-parameter)' },
      },
      {
        scope: ['punctuation', 'meta.brace'],
        settings: { foreground: 'var(--shiki-token-punctuation)' },
      },
      {
        scope: ['string.interpolated.expression'],
        settings: { foreground: 'var(--shiki-token-string-expression)' },
      },
      {
        scope: ['markup.underline.link'],
        settings: { fontStyle: 'underline', foreground: 'var(--shiki-token-link)' },
      },
    ],
    type: 'dark',
  };

// https://vitepress.dev/reference/site-config
export default defineConfig({
  cleanUrls: true,
  description: 'A Python library to simplify common programming tasks.',
  head: [['link', { href: '/icon.svg', rel: 'icon' }]],
  markdown: { theme: customTheme },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: '/icon.svg',
    nav: [
      { link: '/', text: 'Home' },
      { link: sidebar[0]?.items[0]?.link || '/', text: 'Docs' },
    ],
    outline: [2, 4],
    sidebar,
    socialLinks: [{ icon: 'github', link: 'https://github.com/xulbux/python-lib-xulbux' }],
  },
  title: 'XulbuX',
});
