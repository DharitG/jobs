# JobBright UI 2.0 Design System

This document outlines the design system for JobBright UI 2.0, intended for a React / Next.js + Tailwind CSS (with shadcn/ui) codebase. It prioritizes clarity, trust, and conversion.

## 1. Foundation Tokens

### Colors

| Token          | Value     | Rationale                                       |
| :------------- | :-------- | :---------------------------------------------- |
| Primary 500    | `#3E6DFF` | Eye-catching cobalt = "action"                  |
| Primary 600    | `#345BDB` | Hover/active state for Primary 500            |
| Accent/Success | `#18B26E` | "Got an interview" flash moments                |
| Warning        | `#F8A315` | Visa deadlines, quota alerts                    |
| Error          | `#E34C4C` | Failed submit, payment issues                   |
| Grey 00        | `#FFFFFF` | Base white                                      |
| Grey 05        | `#F7F8FC` | Application background                          |
| Grey 20        | `#E1E4F0` | Dividers                                        |
| Grey 40        | `#B6BDD4` | Secondary text                                  |
| Grey 90        | `#12172B` | Main text                                       |

### Shadows

| Token              | Value                             | Usage         |
| :----------------- | :-------------------------------- | :------------ |
| Shadow Elevation 1 | `0 1px 4px rgba(18,23,43,0.08)` | Cards/buttons |

### Radii

*   **Default:** `0.75rem` (12px) - Applied consistently for a friendly yet professional look.

### Spacing

*   **Scale:** `2px` → `4px` → `8px` → `12px` → `16px` → `24px` → `32px` - Ensures consistent rhythm.

### Typography

*   **Sans Serif Font:** `"Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI"`
*   **Display Font (Headings):** `"Satoshi", "Inter", sans-serif`

| Text Role | Size / Weight   | Line Height |
| :-------- | :-------------- | :---------- |
| h1        | 2.25rem / 700   | 1.2         |
| h2        | 1.75rem / 700   | 1.25        |
| h3        | 1.375rem / 600  | 1.3         |
| body-lg   | 1rem / 500      | 1.55        |
| body      | 0.9375rem / 400 | 1.55        |
| caption   | 0.8125rem / 400 | 1.4         |

## 2. Component Catalogue

### 2.1 Atoms

*   **Button (`<Button variant="...">`)**
    *   `default`: (Primary Action) Filled `bg-primary-500`, white text (`text-primary-foreground`), `shadow-1`. Raises slightly on hover (`hover:translate-y-[-1px]`, intensified shadow). Uses `primary-600` for hover background.
    *   `secondary`: `bg-secondary` (Grey 05/10?), `text-secondary-foreground` (Grey 90), `border`. Hover: `bg-accent` (Grey 20?).
    *   `outline`: Transparent background, `border border-input` (Grey 20?), `text-primary-500`. Hover: `bg-accent` (Grey 05?), `text-accent-foreground` (Primary 500?).
    *   `ghost`: Transparent background, `text-grey-90`. Hover: `bg-accent` (Grey 05?), `text-primary-500`.
    *   `destructive`: (Error/Danger) Filled `bg-error`, `text-destructive-foreground` (white). Hover: `bg-error/90`.
    *   `link`: Transparent background, `text-primary-500`, underline on hover.
*   **Input:** Standard input style. Focus: `ring-2 ring-ring ring-offset-2` (using `primary-500/40` for the ring color). Error state: `ring-destructive`.
*   **Badge:** Pill shape (`rounded-full`), small uppercase text, `font-semibold`.
*   **Tooltip:** `rounded-lg` (10px), dark background (`rgba(18,23,43,0.9)`), `200ms` fade animation.

### 2.2 Molecules

*   **JobCard:**
    *   3-column grid: Logo (56x56px), Job Metadata, Right-side CTA.
    *   Company name: `font-bold`. Job title: `font-normal`. Location: `text-grey-40`.
    *   Hover: `outline outline-1 outline-primary-500/20`, slight lift (`translate-y-[-1px]`).
*   **ProgressMeter:**
    *   Horizontal bar segmented (Applied, Screening, Interview, Offer).
    *   Animated gradient sweep indicates stage completion.
*   **QuotaRing:**
    *   Circular progress indicator using `conic-gradient` from `primary-500` to `grey-20`.
    *   Center displays remaining quota count (`{remaining}`).
*   **CTA Banner:**
    *   Striped glassmorphic background (`backdrop-blur-lg`, `bg-white/20`).
    *   Text: "🔒 Unlimited auto-apply".
    *   Large "Upgrade" button (`variant="default"`).

### 2.3 Organisms

*   **Application Pipeline Board:**
    *   Kanban layout using `dnd-kit` for drag-and-drop JobCards.
    *   Sticky column headers with item count badges.
    *   Drop shadow appears on scroll.
*   **VisaPulse Timeline:**
    *   Vertical timeline with status dots (info/warning colors).
    *   Collapsible items for daily entries.
    *   Inline "Book Lawyer" button.
*   **Paywall Modal:**
    *   Max width `640px`.
    *   Dual-column layout: Benefits list (left), Price card (right).
    *   Subtle confetti animation on successful upgrade.

### 2.4 Template Pages

| Page             | Key UI Regions                                                                 |
| :--------------- | :----------------------------------------------------------------------------- |
| **Dashboard**    | Top Nav (Logo, Quota Ring, Upgrade Chip), Left Sidebar (Collapsible), Main Grid (Pipeline + Insights) |
| **Onboarding**   | Step Progress Bar, Content Pane, Persistent "Skip for now" link                |
| **Pricing**      | Segment Control (Monthly/Annual), Tier Cards, FAQ Accordion                    |

## 3. Interaction Design & Motion

*   **Default Transition:** `120ms ease-out-cubic` for interactive elements.
*   **Pipeline Animation:** Spring animation (`stiffness: 200`, `damping: 20`) for column changes.
*   **Loading States:** Skeleton loaders with shimmer effect on dashboard during data fetching.
*   **Toasts:** Slide in from bottom-right. Success: `bg-accent`. Error: `bg-error`.

## 4. Accessibility & Responsiveness

*   **Color Contrast:** AA compliant (4.5:1 for body, 3:1 for large text).
*   **Focus Rings:** Solid `2px primary-500` ring with `2px` offset.
*   **Breakpoints:** `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`.
*   **Mobile:** Bottom tab bar replaces sidebar navigation. Sticky "Upgrade" button.
*   **Keyboard Navigation:** Kanban board navigable (`Cmd + Left/Right` for columns).

## 5. Implementation Files

```plaintext
frontend/
└─ src/
   ├─ styles/
   │   ├─ tailwind.config.ts   # tokens, extend colors, fontFamily
   │   └─ globals.css          # resets, body bg-grey-5
   ├─ components/ui/          # shadcn/ui components
   │   ├─ button.tsx
   │   ├─ input.tsx
   │   ├─ badge.tsx
   │   └─ tooltip.tsx
   │   └─ ...                 # Other shadcn components
   ├─ components/             # Custom composite components
   │   ├─ JobCard.tsx
   │   ├─ ProgressMeter.tsx
   │   ├─ QuotaRing.tsx
   │   ├─ PipelineBoard.tsx
   │   ├─ VisaPulse.tsx
   │   └─ PaywallModal.tsx
   │   └─ ...
   └─ app/                    # Next.js App Router structure
       └─ ...
```

## 6. Tailwind Configuration Snippet

```typescript
// tailwind.config.ts / tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  // ... other shadcn/ui config
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))", // Typically Grey 20 equivalent
        input: "hsl(var(--input))",   // Typically Grey 20 equivalent
        ring: "hsl(var(--ring))",     // Typically Primary 500/40 equivalent
        background: "hsl(var(--background))", // Typically Grey 05
        foreground: "hsl(var(--foreground))", // Typically Grey 90
        primary: {
          DEFAULT: "hsl(var(--primary))", // #3E6DFF
          foreground: "hsl(var(--primary-foreground))", // White
          600: "#345BDB", // Keep for specific hover if needed
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))", // Typically Grey 10/20
          foreground: "hsl(var(--secondary-foreground))", // Typically Grey 90
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))", // #E34C4C
          foreground: "hsl(var(--destructive-foreground))", // White
        },
        muted: {
          DEFAULT: "hsl(var(--muted))", // Typically Grey 20
          foreground: "hsl(var(--muted-foreground))", // Typically Grey 40
        },
        accent: {
          DEFAULT: "hsl(var(--accent))", // #18B26E (Success) or Grey 10/20 for hover
          foreground: "hsl(var(--accent-foreground))", // White or Grey 90
        },
        warning: { // Custom addition
          DEFAULT: "#F8A315",
          foreground: "#12172B", // Dark text for contrast
        },
        popover: {
          DEFAULT: "hsl(var(--popover))", // White
          foreground: "hsl(var(--popover-foreground))", // Grey 90
        },
        card: {
          DEFAULT: "hsl(var(--card))", // White
          foreground: "hsl(var(--card-foreground))", // Grey 90
        },
        grey: { // Keep custom greys if needed beyond shadcn defaults
          5: "#F7F8FC",
          20: "#E1E4F0",
          40: "#B6BDD4",
          90: "#12172B",
        },
      },
      borderRadius: {
        lg: "var(--radius)", // Use shadcn radius variable (0.75rem)
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "sans-serif"], // Use CSS variable
        display: ["Satoshi", "var(--font-sans)", "sans-serif"], // Add Satoshi
      },
      boxShadow: {
         '1': "0 1px 4px rgba(18,23,43,0.08)", // Keep custom shadow if needed
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
  // ... rest of shadcn/ui config (darkMode, content paths)
}
```
*Note: The Tailwind config snippet assumes you are using CSS variables as recommended by `shadcn/ui`. You'll need to define these variables (e.g., in `globals.css`) based on the color palette.*

## 7. Voice, Micro-copy & Branding Lines

| Situation             | Copy                                                                 | Psychological Nudge             |
| :-------------------- | :------------------------------------------------------------------- | :------------------------------ |
| Hero                  | "Stop applying. Start interviewing."                                 | Pain inversion                  |
| Sub-hero              | "50 fully-tailored applications in the next hour—while you grab coffee." | Time save                       |
| Upgrade CTA           | "Unlock unlimited momentum →"                                        | Momentum framing                |
| Empty State (Pipeline)| "No jobs here (yet). Let’s change that—add your first search."       | Encouraging, forward-looking    |
| Success Toast         | "🎉 Interview booked! We’ll handle prep."                            | Instant gratification           |

### Tone Principles

*   **Direct:** Use "You" sentences, lead with verbs.
*   **Positive Friction:** Explain the next step clearly to reduce user overwhelm.
*   **Micro-celebrations:** Use confetti, checkmarks, etc., to reinforce progress.

## 8. Asset Guidelines

*   **Logo:** Simple "JobBright" wordmark + spark icon (angled 15°) in `primary-500`.
*   **Illustrations:** 2D line art with cobalt accents (e.g., from Blush library).
*   **Icon Set:** Lucide icons (24px, stroke width 1.5). Custom fill icons for status dots.
*   **Screenshots/Mockups:** Place within isometric cards using `shadow-1`.

### Quick Wins for Conversion

*   Display sticky "Upgrade" banner only after 30 free applications are submitted.
*   Isolate primary CTAs (`bg-primary-500`) – avoid placing near other blue elements.
*   Include a trust seals row (universities, partners) below the hero section using `text-grey-40` logos.
