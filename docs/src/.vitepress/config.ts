import { exec } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitepress';

const dirname = path.dirname(fileURLToPath(import.meta.url)),
  sidebar = JSON.parse(fs.readFileSync(path.resolve(dirname, 'sidebar.json'), 'utf8'));

function syncPlugin() {
  return {
    configureServer(server: {
      watcher: {
        add: (path: string) => void;
        on: (event: string, cb: (eventName: string, filePath: string) => void) => void;
      };
      restart: () => void;
    }) {
      const srcDir = path.resolve(dirname, '../../src');
      server.watcher.add(srcDir);
      server.watcher.on('all', (eventName: string, filePath: string) => {
        if (filePath.startsWith(srcDir)) {
          const dest = filePath.replace(srcDir, path.resolve(dirname, '../'));
          if (eventName === 'add' || eventName === 'change') {
            fs.mkdirSync(path.dirname(dest), { recursive: true });
            if (filePath.endsWith('.md')) {
              exec(
                `python scripts/build_docs.py --process-file "${filePath}" "${dest}"`,
                { cwd: path.resolve(dirname, '../../..') },
                (err, stdout, stderr) => {
                  if (err) {
                    console.error(err, stderr);
                  } else {
                    console.log(`[sync] Processed ${path.basename(dest)}`);
                    server.restart();
                  }
                }
              );
            } else {
              fs.copyFileSync(filePath, dest);
            }
          } else if (eventName === 'unlink') {
            if (fs.existsSync(dest)) {
              fs.unlinkSync(dest);
            }
          }
        }
      });
    },
    name: 'sync-docs-src',
  };
}

// https://vitepress.dev/reference/site-config
export default defineConfig({
  cleanUrls: true,
  description: 'A Python library to simplify common programming tasks.',
  head: [['link', { href: '/icon.svg', rel: 'icon' }]],
  markdown: { theme: { dark: 'github-dark', light: 'github-light' } },
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
  vite: { plugins: [syncPlugin()] },
});
