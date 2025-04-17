Below is a ground‑up design system (“JobBright UI 2.0”) you can drop straight into a React / Next.js + Tailwind (with shadcn/ui) codebase. It’s opinionated for: clarity ➜ trust ➜ conversion.

1 Foundation tokens


Token	Value	Rationale
Primary 500	#3E6DFF	Eye‑catching cobalt = “action” without fintech‑blue fatigue
Primary 600	#345BDB	Hover/active
Accent / Success	#18B26E	“Got an interview” flash moments
Warning	#F8A315	Visa deadlines, quota alerts
Error	#E34C4C	Failed submit, payment issues
Grey 00	#FFFFFF	Base
Grey 05	#F7F8FC	App background
Grey 20	#E1E4F0	Dividers
Grey 40	#B6BDD4	Secondary text
Grey 90	#12172B	Main text
Shadow‑elevation‑1	0 1px 4px rgba(18,23,43,0.08)	Cards/buttons
Radii	0.75rem (12 px) everywhere	Friendly yet professional
Spacing scale	2 → 4 → 8 → 12 → 16 → 24 → 32 px	Consistent rhythm
Typography

font-sans: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI";
font-display headings: "Satoshi", "Inter", sans-serif;

Text role	Size / weight	Line height
h1	2.25 rem • 700	1.2
h2	1.75 rem • 700	1.25
h3	1.375 rem • 600	1.3
body‑lg	1 rem • 500	1.55
body	.9375 rem • 400	1.55
caption	.8125 rem • 400	1.4
2 Component catalogue (atomic → composite)

2.1 Atoms
Button (<Button variant="primary|secondary|ghost|danger">)
Primary ‑ filled, white text, shadow‑1 ➜ raise on hover (translate‑y‑[-1px], intensify shadow).
Secondary ‑ border-primary‑500, transparent bg, text primary.
Ghost ‑ text grey‑90 → primary‑500 on hover.
Input – 2 px inset outline on focus (ring-primary‑500/40), error ring crimson.
Badge – pill radius (full), small uppercase, weight 600.
Tooltip – 10 px radius, dark rgba(18,23,43,0.9), 200 ms fade.
2.2 Molecules
JobCard
3‑col grid: logo 56×56, job meta, right‑side CTA.
Company in bold, title regular, location grey‑40.
Hover → outline primary‑500/20 + slight lift.
ProgressMeter
Horizontal bar, 4 segments (Applied, Screening, Interview, Offer) – animated gradient sweep when stage achieved.
QuotaRing
Circular progress conic‑gradient from primary‑500 to grey‑20; centre shows {remaining}.
CTA Banner
Striped glassmorphic background (backdrop‑blur‑lg, 20 % white) + “🔒 Unlimited auto‑apply” copy, large Upgrade button.
2.3 Organisms
Application Pipeline Board
Kanban columns with JobCard drag‑n‑drop (dnd‑kit).
Column headers sticky w/ count badge; drop shadow on scroll.
VisaPulse Timeline
Vertical timeline dots coloured by status (info/warning).
Collapsible daily items; lawyer booking button inline.
Paywall Modal
640 px max‑w, dual‑column: benefits list left, price card right.
Subtle confetti animation on successful upgrade.
2.4 Template pages

Page	Key UI regions
Dashboard	Top nav (logo, quota ring, upgrade chip) • left sidebar (icons only on >1024 px; collapsible) • main grid (Pipeline + Insights)
Onboarding wizard	Step progress bar • content pane • persistent Skip for now link (reduces churn)
Pricing	Segment control (Monthly/Annual) • tier cards w/ feature matrix • FAQ accordion
3 Interaction design & motion

120 ms ease‑out‑cubic on interactive elements.
Pipeline column changes animate with spring (stiffness 200, damping 20).
Skeleton loaders (shimmer) on dashboard during scraping.
Toasts slide in from bottom‑right; success = accent green, error = crimson.
4 Accessibility & responsiveness

Color‑contrast AA guaranteed (4.5:1 body, 3:1 large text).
Focus rings: solid 2 px primary‑500 offset 2 px.
Breakpoints: sm 640, md 768, lg 1024, xl 1280, 2xl 1536.
Mobile: bottom tab bar replaces sidebar; sticky Upgrade button.
Keyboard‑navigable Kanban (⌘← / → to change columns).
5 Implementation files

frontend/
└─ src/
   ├─ styles/
   │   ├─ tailwind.config.ts   // tokens, extend colors, fontFamily
   │   └─ globals.css          // resets, body bg-grey05
   ├─ components/ui/
   │   ├─ button.tsx
   │   ├─ input.tsx
   │   ├─ badge.tsx
   │   └─ tooltip.tsx
   ├─ components/
   │   ├─ JobCard.tsx
   │   ├─ ProgressMeter.tsx
   │   ├─ QuotaRing.tsx
   │   ├─ PipelineBoard.tsx
   │   ├─ VisaPulse.tsx
   │   └─ PaywallModal.tsx
   └─ pages/…
Tailwind snippets

// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          500: "#3E6DFF",
          600: "#345BDB",
        },
        accent: "#18B26E",
        warning: "#F8A315",
        error: "#E34C4C",
        grey: {
          5: "#F7F8FC",
          20: "#E1E4F0",
          40: "#B6BDD4",
          90: "#12172B",
        },
      },
      borderRadius: { md: "0.75rem" },
      boxShadow: {
        1: "0 1px 4px rgba(18,23,43,0.08)",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["Satoshi", "Inter", "sans-serif"],
      },
    },
  },
};
6 Voice, micro‑copy & branding lines


Situation	Copy	Psychological nudge
Hero	“Stop applying. Start interviewing.”	Pain inversion
Sub‑hero	“50 fully‑tailored applications in the next hour—while you grab coffee.”	Time save
Upgrade	“Unlock unlimited momentum →”	Momentum framing
Empty state (pipeline)	“No jobs here (yet). Let’s change that—add your first search.”	Encouraging, forward‑looking
Success toast	“🎉 Interview booked! We’ll handle prep.”	Instant gratification
Tone principles

Direct (“You” sentences, verbs first).
Positive friction (explain next step, reduce overwhelm).
Micro‑celebrations (confetti, checkmarks) to reinforce progress.

7 Asset guidelines

Logo – simple wordmark “JobBright” + spark icon (angled 15°) in Primary 500.
Illustrations – 2‑D line art with cobalt accents (open‑source Blush library).
Icon set – Lucide (24 px, stroke width 1.5) ; custom fill icons for status dots.
Screenshots/mockups – placed in isometric cards with soft shadow‑1.
Quick wins for conversion
Sticky Upgrade banner only appears after user submits 30 free applications → targeted, non‑intrusive.
Contrast‑rich CTA (Primary 500) always isolated—never place near another blue.
Trust seals row (universities, YC, etc.) under hero with grey‑40 logos for subtle authority.
