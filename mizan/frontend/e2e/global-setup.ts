import { execSync } from 'node:child_process'
import { writeFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

const API_URL = process.env.API_URL ?? 'http://localhost:8000'
const FRONTEND_URL = process.env.BASE_URL ?? 'http://localhost:5173'
const AUTH_STATE_PATH = resolve(__dirname, 'fixtures', 'auth-state.json')

// Demo admin credentials (from seed.py — idempotent)
const TEST_EMAIL = 'demo-admin@mizan.local'
const TEST_PASSWORD = 'demo_admin_2026'

async function globalSetup() {
  console.log('[global-setup] Seeding database...')

  // Run seed scripts. Use Docker Compose exec if available, else direct Python.
  // Seeds are idempotent — safe to run on every test invocation.
  const seedCommands = [
    'docker compose exec -T backend python scripts/seed.py',
    'docker compose exec -T backend python scripts/seed_content.py',
    'docker compose exec -T backend python scripts/seed_jhsc.py',
  ]

  for (const cmd of seedCommands) {
    try {
      execSync(cmd, {
        cwd: resolve(__dirname, '..', '..'),  // mizan/ directory
        stdio: 'pipe',
        timeout: 120_000,  // JHSC seed can take a while on first run
      })
      console.log(`[global-setup] OK: ${cmd.split(' ').pop()}`)
    } catch (err) {
      console.warn(`[global-setup] Seed command failed (may already be seeded): ${cmd}`)
      // Non-fatal — data may already exist from a prior run
    }
  }

  console.log('[global-setup] Obtaining auth token...')

  // POST /auth/login to get JWT
  const loginResponse = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: TEST_EMAIL, password: TEST_PASSWORD }),
  })

  if (!loginResponse.ok) {
    throw new Error(
      `[global-setup] Login failed: ${loginResponse.status} ${await loginResponse.text()}`
    )
  }

  const { access_token } = (await loginResponse.json()) as { access_token: string }

  if (!access_token) {
    throw new Error('[global-setup] No access_token in login response')
  }

  console.log('[global-setup] Token obtained. Writing auth state...')

  // Write storageState JSON — Playwright reads this to inject localStorage
  const storageState = {
    cookies: [],
    origins: [
      {
        origin: FRONTEND_URL,
        localStorage: [
          { name: 'mizan_token', value: access_token },
        ],
      },
    ],
  }

  // Ensure fixtures directory exists
  mkdirSync(resolve(__dirname, 'fixtures'), { recursive: true })

  writeFileSync(AUTH_STATE_PATH, JSON.stringify(storageState, null, 2), 'utf-8')

  console.log(`[global-setup] Auth state written to ${AUTH_STATE_PATH}`)
}

export default globalSetup
