import { exec } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

export function syncPlugin(dirname: string) {
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
