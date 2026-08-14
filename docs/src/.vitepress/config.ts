import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitepress';

const dirname = path.dirname(fileURLToPath(import.meta.url)),
  sidebar = JSON.parse(fs.readFileSync(path.resolve(dirname, 'sidebar.json'), 'utf8'));

// https://vitepress.dev/reference/site-config
export default defineConfig({
  cleanUrls: true,
  description: 'A Python library to simplify common programming tasks.',
  head: [['link', { href: '/icon.svg', rel: 'icon' }]],
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
