# Phase 11: Onboarding Tour - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a Driver.js-powered guided onboarding tour triggered by a help button in the Layout header. The tour walks new users through the 3 platform sections (Observatory, Bias Auditor, Training) on the Dashboard page. First-time users see it automatically; returning users trigger it via the help button.

</domain>

<decisions>
## Implementation Decisions

### Help Button Design
- Placed in the Layout header bar, between user name and logout button
- Outlined circle with (?) icon, white to match header text
- Arabic tooltip on hover: "جولة تعريفية"
- Gentle CSS pulse animation on the button for first-time users only (disappears after tour seen)

### Tour Scope & Navigation
- Tour stays on the Dashboard page only — no cross-page navigation
- Full walkthrough: 5-6 steps covering Welcome → Header/logo → Nav tabs → Observatory card → Bias Auditor card → Training card
- Final step ends with a CTA suggesting "Start with Training" (the most interactive section)
- Skip button ("تخطي") appears on every step alongside Next/Previous

### Tour Step Content
- Friendly and conversational Arabic tone (e.g., "مرحباً! دعنا نعرفك على المنصة.")
- Each card step mentions the persona name (e.g., "هذا قسم رانيا — مسؤولة السياسات. تابعي اتجاهات خطاب الكراهية.")
- Generic welcome — no hackathon-specific context (works for any audience)
- 1-2 sentences per step — enough to explain purpose without overwhelming

### First-Time Detection
- localStorage flag: `mizan_tour_seen=true` set after tour completes or is dismissed
- Auto-trigger: tour starts ~500ms after Dashboard loads for first-time users
- Dismissing/skipping counts as "seen" — no nagging on repeat visits
- Help button always re-runs the full tour (no short/full option)

### Claude's Discretion
- Exact Driver.js configuration (overlay opacity, animation speed, popover positioning)
- Step highlight element selectors (CSS selectors for each tour target)
- Button labels (Next/Previous/Skip Arabic text)
- Color theme for Driver.js popovers (match mizan-navy or use defaults)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Layout.tsx`: Shared shell with header + nav — help button goes in the header `<div className="flex items-center gap-4">` section
- `Dashboard.tsx`: 3 persona cards with `data-testid`-able structure — cards are Link elements in a `grid grid-cols-3` container
- `useAuth()` hook: Provides `user` object — available for personalization if needed

### Established Patterns
- Tailwind CSS v3.4 for all styling — RTL via logical properties (ms-, me-, ps-, pe-)
- Tajawal font via `font-tajawal` class
- `mizan-navy` custom color used throughout header/nav
- React Router `<Link>` for navigation, `useLocation` for active tab detection

### Integration Points
- Layout.tsx header section: Insert help button between user name span and logout button
- Dashboard.tsx: Add data attributes or IDs to cards for Driver.js step targeting
- App.tsx: OnboardingTour component wraps or sits inside Layout/Dashboard

</code_context>

<specifics>
## Specific Ideas

- Personas reinforce the hackathon story: "هذا قسم رانيا" / "هذا قسم لينا" / "هذا قسم خالد"
- Final CTA guides to Training — the demo's most interactive section
- Pulse animation draws attention to (?) on first visit without being obnoxious

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-onboarding-tour*
*Context gathered: 2026-03-03*
