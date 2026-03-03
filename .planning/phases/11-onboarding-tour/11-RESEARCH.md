# Phase 11: Onboarding Tour - Research

**Researched:** 2026-03-03
**Domain:** Driver.js guided tour integration, React RTL UI, localStorage persistence
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Help Button Design**
- Placed in the Layout header bar, between user name and logout button
- Outlined circle with (?) icon, white to match header text
- Arabic tooltip on hover: "جولة تعريفية"
- Gentle CSS pulse animation on the button for first-time users only (disappears after tour seen)

**Tour Scope & Navigation**
- Tour stays on the Dashboard page only — no cross-page navigation
- Full walkthrough: 5-6 steps covering Welcome → Header/logo → Nav tabs → Observatory card → Bias Auditor card → Training card
- Final step ends with a CTA suggesting "Start with Training" (the most interactive section)
- Skip button ("تخطي") appears on every step alongside Next/Previous

**Tour Step Content**
- Friendly and conversational Arabic tone (e.g., "مرحباً! دعنا نعرفك على المنصة.")
- Each card step mentions the persona name (e.g., "هذا قسم رانيا — مسؤولة السياسات.")
- Generic welcome — no hackathon-specific context
- 1-2 sentences per step — enough to explain purpose without overwhelming

**First-Time Detection**
- localStorage flag: `mizan_tour_seen=true` set after tour completes or is dismissed
- Auto-trigger: tour starts ~500ms after Dashboard loads for first-time users
- Dismissing/skipping counts as "seen" — no nagging on repeat visits
- Help button always re-runs the full tour (no short/full option)

### Claude's Discretion
- Exact Driver.js configuration (overlay opacity, animation speed, popover positioning)
- Step highlight element selectors (CSS selectors for each tour target)
- Button labels (Next/Previous/Skip Arabic text)
- Color theme for Driver.js popovers (match mizan-navy or use defaults)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UI-04 (new) | Help-button-triggered onboarding tour using Driver.js that walks users through the 3 platform tools — reducing time-to-first-action for new users | Driver.js v1.4.0 confirmed available on npm; tour API (drive(), destroy(), onDestroyed) maps directly to auto-trigger + help-button re-run + seen flag persistence; CSS customization enables mizan-navy theming and Tajawal font match |
</phase_requirements>

---

## Summary

Driver.js v1.4.0 is the locked library. It is a dependency-free vanilla JS library that works cleanly inside React via a custom hook — no React-specific wrapper package is needed or recommended. The API surface needed for this phase is small: `driver()` constructor, `drive()` to start, `destroy()` to end, and `onDestroyed` callback to set the localStorage flag. The library ships its own CSS file (`driver.js/dist/driver.css`) that must be imported once in the React entry point or the component, and its popover elements are standard DOM nodes styled with overridable CSS class selectors.

The tour stays on the Dashboard page only, which simplifies implementation significantly — all step target elements (header logo, nav bar, three persona cards) are present in the DOM whenever the Dashboard renders. No cross-page navigation or step deferral is required. The `OnboardingTour` component will be a React hook (no JSX DOM of its own) that manages the driver instance lifecycle, and the help button lives in `Layout.tsx`. The `mizan_tour_seen` localStorage flag is the only persistence layer; no backend changes are required.

The main RTL consideration is that Driver.js renders popovers in a separate DOM layer appended to `<body>`. Since the project sets `html { direction: rtl; }` globally, Driver.js popovers will inherit RTL direction automatically. Arabic button text must be set explicitly via `nextBtnText`, `prevBtnText`, and `doneBtnText` on the driver config. The pulse animation on the help button is pure Tailwind/CSS — no Driver.js involvement.

**Primary recommendation:** Install `driver.js@^1.4.0`, create `src/components/OnboardingTour.tsx` as a custom hook (`useOnboardingTour`) that returns `{ startTour }`, import the driver CSS once in `index.css` or `main.tsx`, add a `data-tour` attribute to each Dashboard card for stable step targeting, wire the help button in `Layout.tsx` to `startTour()`, and use a `useEffect` in `Dashboard.tsx` to auto-trigger on first visit.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| driver.js | ^1.4.0 | Guided product tour with overlay, popover, and step navigation | Locked user decision; no dependencies, ships TS types, 12KB gzip, CSS customizable |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none) | — | Driver.js has no peer deps | — |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| driver.js | intro.js | intro.js is older, heavier, and not the locked decision |
| driver.js | react-joyride | React-specific wrapper; overkill for this use case and not the locked decision |

**Installation:**
```bash
npm install driver.js
```

No `@types/driver.js` package needed — driver.js v1.x ships its own TypeScript declarations in the package.

---

## Architecture Patterns

### Recommended Project Structure
```
src/
├── components/
│   └── OnboardingTour.tsx   # Custom hook: useOnboardingTour() → { startTour }
├── pages/
│   └── Dashboard.tsx        # Adds data-tour IDs to cards; calls useOnboardingTour
├── components/
│   └── Layout.tsx           # Help button (?) wired to startTour
└── index.css                # Import driver.js/dist/driver.css here (or main.tsx)
```

### Pattern 1: Custom Hook Encapsulating Driver Instance

**What:** `useOnboardingTour()` creates and memoizes a driver instance with all step definitions. Returns `{ startTour }`. The hook lives in `OnboardingTour.tsx` or co-located with `Dashboard.tsx`.

**When to use:** Any React component that needs to trigger the tour calls `startTour()`. Dashboard auto-triggers via `useEffect`. Layout button calls it directly.

**Challenge:** The hook must be invoked on Dashboard (where target elements live), and the start function must be passed up to Layout where the button lives. The cleanest solution for this small scope is a React context or lifting state to `App.tsx`. The recommended approach given the project's existing patterns (no Redux, no Zustand) is a **TourContext** provided at the App level.

```typescript
// Source: Context7 /kamranahmedse/driver.js + project pattern
// src/components/OnboardingTour.tsx

import { createContext, useContext, useCallback, useRef, ReactNode } from 'react'
import { driver, Driver } from 'driver.js'
import 'driver.js/dist/driver.css'

const TOUR_SEEN_KEY = 'mizan_tour_seen'

interface TourContextValue {
  startTour: () => void
}

const TourContext = createContext<TourContextValue>({ startTour: () => {} })

export function TourProvider({ children }: { children: ReactNode }) {
  const driverRef = useRef<Driver | null>(null)

  const startTour = useCallback(() => {
    driverRef.current?.destroy()

    driverRef.current = driver({
      animate: true,
      overlayOpacity: 0.6,
      showProgress: true,
      progressText: '{{current}} / {{total}}',
      allowClose: true,
      nextBtnText: 'التالي ←',
      prevBtnText: '→ السابق',
      doneBtnText: 'ابدأ التدريب',
      popoverClass: 'mizan-tour-popover',
      steps: [
        {
          popover: {
            title: 'مرحباً بك في ميزان!',
            description: 'دعنا نعرّفك على المنصة في دقيقة واحدة.',
          },
        },
        {
          element: '#tour-logo',
          popover: {
            title: 'منصة ميزان',
            description: 'ميزان هي منصة للذكاء الاصطناعي لرصد خطاب الكراهية العربي وتدريب المشرفين.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-nav',
          popover: {
            title: 'الأقسام الثلاثة',
            description: 'تنقّل بين المرصد ومدقق التحيز والتدريب من هذا الشريط.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-card-observatory',
          popover: {
            title: 'المرصد — رانيا',
            description: 'هذا قسم رانيا — مسؤولة السياسات. تابعي اتجاهات خطاب الكراهية في الأردن على مدى ٨ سنوات.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-card-audit',
          popover: {
            title: 'مدقق التحيز — لينا',
            description: 'هذا قسم لينا — باحثة NLP. قيّمي عدالة النموذج عبر فئات خطاب الكراهية التسع.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-card-training',
          popover: {
            title: 'التدريب — خالد',
            description: 'هذا قسم خالد — مشرف المحتوى. ابدأ هنا! صنّف محتوى عربياً حقيقياً بمساعدة الذكاء الاصطناعي.',
            side: 'bottom',
            align: 'start',
          },
        },
      ],
      onDestroyed: () => {
        localStorage.setItem(TOUR_SEEN_KEY, 'true')
      },
    })

    driverRef.current.drive()
  }, [])

  return (
    <TourContext.Provider value={{ startTour }}>
      {children}
    </TourContext.Provider>
  )
}

export function useTour() {
  return useContext(TourContext)
}

export function isTourSeen(): boolean {
  return localStorage.getItem(TOUR_SEEN_KEY) === 'true'
}
```

### Pattern 2: Auto-trigger in Dashboard via useEffect

**What:** Dashboard checks the localStorage flag on mount and calls `startTour()` with a 500ms delay (per locked decision) if not seen.

```typescript
// Source: locked CONTEXT.md decision + driver.js destroy/drive API
// src/pages/Dashboard.tsx — additions only

import { useEffect } from 'react'
import { useTour, isTourSeen } from '../components/OnboardingTour'

export default function Dashboard() {
  const { startTour } = useTour()

  useEffect(() => {
    if (!isTourSeen()) {
      const timer = setTimeout(() => startTour(), 500)
      return () => clearTimeout(timer)
    }
  }, [startTour])

  // ... existing JSX with data-tour IDs added to cards
}
```

### Pattern 3: Help Button in Layout.tsx

**What:** A `?` button inserted between the user name span and the logout button. Uses `useTour()` to call `startTour()`. Shows a pulse animation when `!isTourSeen()`.

```typescript
// Source: locked CONTEXT.md design decisions
// src/components/Layout.tsx — additions only

import { useTour, isTourSeen } from './OnboardingTour'

// Inside header <div className="flex items-center gap-4">:
const { startTour } = useTour()
const showPulse = !isTourSeen()

<button
  onClick={startTour}
  title="جولة تعريفية"
  className={`w-8 h-8 rounded-full border border-white/60 text-white text-sm font-bold flex items-center justify-center hover:border-white transition-colors ${showPulse ? 'animate-pulse' : ''}`}
  aria-label="جولة تعريفية"
>
  ?
</button>
```

**Note:** `showPulse` should be derived from component state (initialized from `isTourSeen()`) rather than calling `isTourSeen()` directly on each render, so the pulse disappears reactively after the first tour completes. Use `useState<boolean>(!isTourSeen())` in Layout and update it via a `tourStarted` callback or a shared context state field.

### Pattern 4: CSS Override for Tajawal Font

**What:** Driver.js popovers live outside React's DOM but inside `<body>`, so they inherit `html { direction: rtl; }` from `index.css`. Font must be explicitly set in a CSS override since Tailwind utility classes don't reach Driver.js DOM.

```css
/* Append to src/index.css */
.mizan-tour-popover {
  font-family: 'Tajawal', sans-serif;
  direction: rtl;
}

.mizan-tour-popover .driver-popover-title {
  color: #1a1a2e; /* mizan-navy */
  font-size: 1rem;
  font-weight: 700;
}

.mizan-tour-popover .driver-popover-description {
  color: #374151; /* gray-700 */
  font-size: 0.875rem;
  line-height: 1.6;
}

.mizan-tour-popover .driver-popover-navigation-btns button {
  font-family: 'Tajawal', sans-serif;
  background-color: #1a1a2e;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
}

.mizan-tour-popover .driver-popover-navigation-btns button:hover {
  background-color: #2d2d4e;
}
```

### Pattern 5: data-tour IDs for Stable Element Targeting

**What:** Add `id` attributes (not `data-testid` to avoid mixing E2E/tour concerns) to Dashboard cards and Layout elements so Driver.js step selectors are stable regardless of CSS class changes.

Elements to ID:
- `#tour-logo` — the `<Link to="/">` in Layout header
- `#tour-nav` — the `<nav>` element in Layout
- `#tour-card-observatory` — the Observatory `<Link>` card
- `#tour-card-audit` — the Bias Auditor `<Link>` card
- `#tour-card-training` — the Training `<Link>` card

### Anti-Patterns to Avoid

- **Creating driver instance outside React:** Don't create `driver()` at module scope or in an event handler without cleanup. Always use `useRef` to hold the instance so it can be destroyed on re-call.
- **Using CSS class selectors as tour targets:** Dashboard card classes (`rounded-xl`, `border-t-4`, etc.) are shared and fragile. Use unique `id` attributes instead.
- **Importing driver CSS inside the component:** Import once in `index.css` or `main.tsx` to avoid multiple injections.
- **Not calling destroy() before re-triggering:** If the user clicks the help button while a tour is active (e.g., clicked twice), call `driverRef.current?.destroy()` before creating a new instance.
- **Setting `mizan_tour_seen` before tour finishes:** The flag must be set in `onDestroyed`, not when the tour starts — so partial tours don't suppress the auto-trigger incorrectly. Skipping mid-tour still calls `onDestroyed`, so the flag is correctly set on skip too.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Overlay with click-outside-to-close | Custom modal/overlay | driver.js built-in `allowClose: true` + `overlayClickBehavior` | Handles z-index stacking, pointer-events, scroll lock correctly |
| Popover positioning | Custom tooltip with absolute/fixed positioning | driver.js automatic `side`/`align` detection | Handles viewport boundary detection, auto-flip, scroll offset |
| Step focus management | Custom focus trap | driver.js built-in focus management | WCAG-compliant focus trap within each step |
| Keyboard navigation | Custom keydown listener | driver.js built-in `allowKeyboardControl: true` | Escape key, arrow keys handled correctly |

**Key insight:** Tour overlays with popover positioning are surprisingly complex (viewport overflow, scroll containers, z-index wars). Driver.js solves all of this in 12KB.

---

## Common Pitfalls

### Pitfall 1: Pulse Animation Not Disappearing After Tour

**What goes wrong:** Help button shows `animate-pulse` even after the user completes the tour, because `isTourSeen()` reads localStorage only at render time and Layout doesn't re-render after the tour ends.

**Why it happens:** `onDestroyed` fires after the Driver.js overlay teardown — at that point, Layout's render cycle has already completed. React doesn't know to re-render.

**How to avoid:** Store `tourSeen` as a state variable in TourContext (initialized from localStorage). After `onDestroyed` fires, call a context setter `setTourSeen(true)`. Layout reads the context state, not localStorage directly, so it re-renders correctly.

**Warning signs:** Pulse still visible after clicking help → completing tour → returning to dashboard.

### Pitfall 2: Driver.js Steps Targeting Elements Not Yet in DOM

**What goes wrong:** If `drive()` is called before the Dashboard cards render (e.g., during a React Suspense boundary or conditional render), Driver.js silently skips or errors on steps with missing elements.

**Why it happens:** The 500ms `setTimeout` auto-trigger mitigates this for normal renders, but race conditions are possible on slow connections.

**How to avoid:** Use `element: () => document.getElementById('tour-card-observatory')` (function-form selector) so Driver.js evaluates the element lazily at step activation time, not at tour initialization. If element returns `null`, Driver.js skips that step without crashing (confirmed behavior in docs).

**Warning signs:** Tour jumps from step 1 to step 4 unexpectedly.

### Pitfall 3: RTL Arrow Direction in Popovers

**What goes wrong:** Driver.js uses CSS border-triangle arrows to point at highlighted elements. In RTL context, the visual arrow may point in the wrong direction because the library's default CSS assumes LTR.

**Why it happens:** Driver.js CSS is LTR-agnostic for arrows themselves (they're computed geometrically), but button order (next/previous) may feel reversed in an RTL context.

**How to avoid:** Since buttons are labeled in Arabic ("التالي" / "السابق"), the directionality is conveyed by text. The layout order of buttons inside the popover's `driver-popover-navigation-btns` flex container may need a CSS override: `flex-direction: row-reverse` if the "Next" button appears on the left. Test manually.

**Warning signs:** Arabic users see "التالي" (Next) on the left side of the popover button row.

### Pitfall 4: `mizan_tour_seen` Key Collision with Future Auth State

**What goes wrong:** `localStorage.getItem('mizan_tour_seen')` might persist across user logouts — if a second user logs in on the same browser, they won't see the tour.

**Why it happens:** The flag is not scoped per user and is not cleared on logout.

**How to avoid:** For this MVP scope, accept the behavior — the flag is session/browser-scoped, which is acceptable for a demo/hackathon context. Document it as a known limitation. If per-user scoping is needed later, key the flag as `mizan_tour_seen_${userId}`.

**Warning signs:** Shared demo machine shows no tour for second persona.

### Pitfall 5: Import Order for Driver.js CSS

**What goes wrong:** Tailwind's `@tailwind base` resets some styles that Driver.js CSS relies on (e.g., button resets). Importing driver CSS before Tailwind directives causes Driver.js button styles to be overridden by Tailwind's preflight reset.

**Why it happens:** Tailwind preflight resets all button appearance; driver.js button CSS must come after preflight.

**How to avoid:** Import `driver.js/dist/driver.css` in `main.tsx` (not `index.css`), after the `index.css` import. Or append driver CSS overrides at the bottom of `index.css` after the `@tailwind utilities` directive.

```typescript
// src/main.tsx — correct import order
import './index.css'          // @tailwind base/components/utilities
import 'driver.js/dist/driver.css'  // after Tailwind reset
```

---

## Code Examples

Verified patterns from official sources:

### Basic Tour with Steps
```typescript
// Source: Context7 /kamranahmedse/driver.js
import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'

const driverObj = driver({
  showProgress: true,
  steps: [
    { element: '#logo', popover: { title: 'ميزان', description: 'المنصة الرئيسية' } },
    { element: '#nav',  popover: { title: 'التنقل', description: 'الأقسام الثلاثة' } },
  ],
  onDestroyed: () => {
    localStorage.setItem('mizan_tour_seen', 'true')
  },
})
driverObj.drive()
```

### Programmatic Control
```typescript
// Source: Context7 /kamranahmedse/driver.js
driverObj.drive()          // Start from step 0
driverObj.drive(2)         // Start from step index 2
driverObj.isActive()       // Returns boolean
driverObj.destroy()        // End tour, fires onDestroyed
```

### TypeScript Types (built-in)
```typescript
// Source: Context7 /kamranahmedse/driver.js
import { driver, Driver, Config, DriveStep, Popover } from 'driver.js'

const config: Config = {
  steps: [] as DriveStep[],
  onDestroyed: () => {},
}
const driverObj: Driver = driver(config)
```

### CSS Class Override Pattern
```css
/* Source: Context7 /kamranahmedse/driver.js styling guide */
.driver-popover.mizan-tour-popover {
  font-family: 'Tajawal', sans-serif;
  background-color: #ffffff;
}
.driver-popover.mizan-tour-popover .driver-popover-title {
  color: #1a1a2e;
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| intro.js (older standard) | driver.js v1.x | ~2023 | Smaller, TS-native, no jQuery dep |
| Separate `@types/driver.js` | Types bundled in driver.js | v1.0 | No separate type install needed |
| `popoverClass` on global config | Can be set per-step too | v1.0 | Allows mixed themes in one tour |

**Deprecated/outdated:**
- `driver.js` v0.x API: Used a different constructor pattern and had a React wrapper (`react-driver.js`). v1.x is a complete rewrite with cleaner API. Don't reference v0.x docs.

---

## Open Questions

1. **Pulse animation on first-time indicator — Tailwind `animate-pulse` sufficiency**
   - What we know: Tailwind's `animate-pulse` is an opacity pulse, not a ring/glow effect
   - What's unclear: Whether `animate-pulse` alone is visually "gentle" enough, or if a custom `@keyframes` ring animation is preferred
   - Recommendation: Use `animate-pulse` for simplicity (it matches existing Tailwind-only constraint); the planner may add a custom ring keyframe as a Claude's Discretion enhancement

2. **TourContext scope: App-level vs Dashboard-only**
   - What we know: `startTour` is needed in two places — Dashboard (auto-trigger) and Layout (help button)
   - What's unclear: Whether to use React Context or prop-drilling (Layout renders children, not siblings, so context is the right pattern)
   - Recommendation: Wrap `<App>` routes with `<TourProvider>` so both Dashboard and Layout can call `useTour()`. This requires `TourProvider` inside `AuthProvider` and `BrowserRouter`.

---

## Validation Architecture

> `nyquist_validation` is not present in `.planning/config.json` — section included since Playwright E2E tests are the project's established test pattern for UI features.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Playwright 1.58.2 |
| Config file | `mizan/frontend/playwright.config.ts` |
| Quick run command | `npx playwright test e2e/onboarding.spec.ts` |
| Full suite command | `npx playwright test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UI-04 (SC-1) | driver.js installed and import resolves | build/smoke | `npm run build` | ❌ Wave 0 (build check) |
| UI-04 (SC-2) | Help button (?) visible in header on all authenticated pages | E2E | `npx playwright test e2e/onboarding.spec.ts` | ❌ Wave 0 |
| UI-04 (SC-3) | Clicking help button launches tour (Driver.js overlay appears) | E2E | `npx playwright test e2e/onboarding.spec.ts` | ❌ Wave 0 |
| UI-04 (SC-4) | Tour steps contain Arabic descriptions | E2E | `npx playwright test e2e/onboarding.spec.ts` | ❌ Wave 0 |
| UI-04 (SC-5) | `mizan_tour_seen` set after tour completion | E2E | `npx playwright test e2e/onboarding.spec.ts` | ❌ Wave 0 |
| UI-04 (SC-5) | First-time users: tour auto-triggers on Dashboard load | E2E (localStorage clear) | `npx playwright test e2e/onboarding.spec.ts` | ❌ Wave 0 |

### Playwright Testing Note for Driver.js
Driver.js injects DOM elements with classes like `.driver-overlay`, `.driver-popover`, `.driver-popover-title`. These are standard DOM elements queryable by Playwright:
```typescript
// Detect tour is active
await expect(page.locator('.driver-popover')).toBeVisible()
// Read popover title
await expect(page.locator('.driver-popover-title')).toContainText('مرحباً')
// Click next button
await page.locator('.driver-popover-next-btn').click()
// Detect tour closed
await expect(page.locator('.driver-popover')).not.toBeVisible()
```

For testing auto-trigger, the storageState fixture injects `mizan_token` but NOT `mizan_tour_seen`, so first-visit auto-trigger tests work naturally with the existing auth fixture by not pre-setting the flag.

### Sampling Rate
- **Per task commit:** `npx playwright test e2e/onboarding.spec.ts`
- **Per wave merge:** `npx playwright test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mizan/frontend/e2e/onboarding.spec.ts` — covers all UI-04 success criteria

*(No framework install needed — Playwright is already installed)*

---

## Sources

### Primary (HIGH confidence)
- `/kamranahmedse/driver.js` (Context7) — driver() constructor, step configuration, TypeScript types, CSS override patterns, onDestroyed callback, localStorage persistence pattern, highlight API, destroy API
- `npm info driver.js version` — confirmed 1.4.0 is the latest stable version (verified 2026-03-03)
- Project files read directly: `Layout.tsx`, `Dashboard.tsx`, `App.tsx`, `package.json`, `tailwind.config.js`, `index.css`, `playwright.config.ts`, `global-setup.ts`, `dashboard.spec.ts`, `auth.spec.ts`

### Secondary (MEDIUM confidence)
- Context7 /kamranahmedse/driver.js styling guide — CSS class names (`.driver-popover`, `.driver-popover-title`, `.driver-popover-navigation-btns`) confirmed via official docs source in Context7

### Tertiary (LOW confidence)
- RTL arrow direction behavior — not explicitly documented; inferred from CSS border-triangle geometry and global `html { direction: rtl }` inheritance. Flagged for manual testing.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — driver.js v1.4.0 confirmed on npm, TypeScript types bundled, API verified via Context7
- Architecture: HIGH — React hook pattern + Context API is standard React; driver.js API verified; localStorage pattern confirmed via official driver.js docs example
- Pitfalls: MEDIUM-HIGH — CSS pitfalls verified via Tailwind/driver.js interaction analysis; RTL arrow pitfall is LOW confidence (requires manual verification)

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (driver.js is stable; React 18 patterns are stable)
