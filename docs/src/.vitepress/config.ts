import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitepress';

const dirname = path.dirname(fileURLToPath(import.meta.url)),
  sidebar = JSON.parse(fs.readFileSync(path.resolve(dirname, 'sidebar.json'), 'utf8'));

// https://vitepress.dev/reference/site-config
export default defineConfig({
  cleanUrls: true,
  description: 'Advanced Python Library',
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { link: '/', text: 'Home' },
      { link: sidebar[0]?.items[0]?.link || '/', text: 'API Reference' },
    ],
    sidebar,
    socialLinks: [{ icon: 'github', link: 'https://github.com/xulbux/python-lib-xulbux' }],
  },
  title: 'xulbux',
  vite: { plugins: [tailwindcss()] },
});
