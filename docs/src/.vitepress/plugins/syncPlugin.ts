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
      const pySrcDir = path.resolve(dirname, '../../../src');

      server.watcher.add(srcDir);
      server.watcher.add(pySrcDir);

      server.watcher.on('all', (eventName: string, filePath: string) => {
        const isPySrc = filePath.startsWith(pySrcDir) && filePath.endsWith('.py');
        const isDocsSrc = filePath.startsWith(srcDir);

        if (!isPySrc && !isDocsSrc) {
          return;
        }

        function runPythonCommand(args: string[], successMsg: string, restartServer = false) {
          function run(commands: string[]) {
            exec(
              `${commands[0]} ${args.join(' ')}`,
              { cwd: path.resolve(dirname, '../../..') },
              (err, stdout, stderr) => {
                if (err) {
                  if (commands.length > 1) {
                    run(commands.slice(1));
                  } else {
                    // oxlint-disable-next-line no-console
                    console.error(err, stderr);
                  }
                } else {
                  // oxlint-disable-next-line no-console
                  console.log(`[sync] ${successMsg}: ${path.basename(filePath)}`);
                  if (restartServer) {
                    server.restart();
                  }
                }
              }
            );
          }
          run(['python', 'py', 'python3']);
        }

        if (isDocsSrc) {
          const dest = filePath.replace(srcDir, path.resolve(dirname, '../'));
          if (eventName === 'add' || eventName === 'change') {
            fs.mkdirSync(path.dirname(dest), { recursive: true });
            if (filePath.endsWith('.md')) {
              runPythonCommand(
                ['docs/build.py', '--process-file', `"${filePath}"`],
                'Processed MD',
                false
              );
            } else {
              fs.copyFileSync(filePath, dest);
              if (filePath.endsWith('sidebar.json')) {
                runPythonCommand(
                  ['docs/build.py'],
                  'Rebuilt docs due to sidebar.json change',
                  true
                );
              }
            }
          } else if (eventName === 'unlink') {
            if (fs.existsSync(dest)) {
              fs.unlinkSync(dest);
            }
            if (filePath.endsWith('sidebar.json')) {
              runPythonCommand(['docs/build.py'], 'Rebuilt docs due to sidebar.json unlink', true);
            } else if (filePath.endsWith('.md')) {
              runPythonCommand(['docs/build.py'], 'Rebuilt docs due to MD unlink', true);
            }
          }
        } else if (isPySrc) {
          const relPyPath = path.relative(pySrcDir, filePath);
          const parts = relPyPath.split(path.sep);
          if (
            parts.length >= 2 &&
            parts[0] === 'xulbux' &&
            !parts[parts.length - 1].startsWith('_')
          ) {
            if (eventName === 'change') {
              runPythonCommand(
                ['docs/build.py', '--process-file', `"${filePath}"`],
                'Processed Python API',
                false
              );
            } else if (eventName === 'add' || eventName === 'unlink') {
              runPythonCommand(
                ['docs/build.py'],
                `Rebuilt docs due to Python source ${eventName}`,
                true
              );
            }
          }
        }
      });
    },
    name: 'sync-docs-src',
  };
}
