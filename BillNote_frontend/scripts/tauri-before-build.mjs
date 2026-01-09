import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const frontendDir = resolve(__dirname, '..')
const repoRoot = resolve(frontendDir, '..')

const run = (command, args, opts = {}) => {
  const res = spawnSync(command, args, { stdio: 'inherit', ...opts })
  if (res.error) throw res.error
  if (res.status !== 0) process.exit(res.status ?? 1)
}

const buildBackend = () => {
  const isWindows = process.platform === 'win32'
  const script = isWindows ? resolve(repoRoot, 'backend', 'build.bat') : resolve(repoRoot, 'backend', 'build.sh')

  if (!existsSync(script)) {
    throw new Error(`Backend build script not found: ${script}`)
  }

  if (isWindows) {
    const comspec = process.env.COMSPEC || 'cmd.exe'
    run(comspec, ['/d', '/s', '/c', 'backend\\build.bat'], { cwd: repoRoot })
    return
  }

  run('bash', ['-lc', 'chmod +x backend/build.sh && ./backend/build.sh'], { cwd: repoRoot })
}

const buildFrontend = () => {
  const pnpm = process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm'
  run(pnpm, ['build', '--mode', 'tauri'], { cwd: frontendDir })
}

buildBackend()
buildFrontend()

