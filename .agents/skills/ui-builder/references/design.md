# StudyOps Design System

## Overview

StudyOps uses a retro-playful teal, coral, and gold visual system adapted for a focused study-management application.

The design combines vintage warmth with modern web-app usability:

- bold, friendly headings;
- tactile cards and controls;
- rounded shapes;
- colorful status accents;
- soft colored shadows;
- clear visual hierarchy; and
- restrained moments of celebration.

The interface should feel motivating without becoming childish or visually noisy. Deadlines, schedules, forms, tasks, and planning decisions must remain easy to scan.

Implement the design with Tailwind CSS utilities and centrally defined semantic Tailwind theme tokens. Do not repeat raw colors, spacing values, shadows, radii, or inline styles throughout JSX.

## Tailwind token policy

- Define reusable product tokens centrally in the frontend Tailwind theme layer.
- With Tailwind CSS 4, register reusable colors and shadows through the shared theme configuration in `frontend/src/index.css`.
- Use semantic utilities such as `bg-primary`, `text-primary-dark`, `border-accent`, and `shadow-card`.
- Keep raw hexadecimal values inside the central theme definition, not inside components.
- Prefer Tailwind’s standard spacing, typography, radius, and breakpoint scales.
- Introduce a custom token only when it represents a repeated StudyOps design decision.
- Use Tailwind utility classes for ordinary component and page styling.
- Do not use inline `style` objects, CSS modules, or component-specific CSS for ordinary styling.

## Colors

These values define the source palette. Register them as semantic Tailwind color tokens before using them.

| Semantic token | Value | Purpose |
| --- | --- | --- |
| `primary` | `#2BA8A2` | Main brand color, progress, selected controls |
| `primary-light` | `#3CC4BD` | Hover treatments and lighter accents |
| `primary-dark` | `#1E8C86` | Strong brand text, active states, deep surfaces |
| `primary-subtle` | `#E8F6F5` | Selected rows and subtle brand backgrounds |
| `accent` | `#FFD23F` | Primary actions, important highlights, milestones |
| `accent-light` | `#FFE47A` | Soft highlight surfaces |
| `accent-dark` | `#E6B800` | Accent hover and pressed states |
| `coral` | `#EF6C4A` | Urgent tasks, warnings, destructive emphasis |
| `coral-light` | `#FF8A6A` | Soft warning surfaces |
| `coral-dark` | `#D45233` | Strong warning and pressed states |
| `cream` | `#FFF8E7` | Warm input and emphasized card surfaces |
| `sky` | `#5DADE2` | Informational and assistant-related states |
| `surface-base` | `#EFF8F7` | Application background |
| `surface-card` | `#FFFFFF` | Cards, dialogs, menus, and raised surfaces |
| `success` | `#27AE60` | Completed work and successful actions |
| `error` | `#E74C3C` | Errors and destructive feedback |

Use a dark neutral color for ordinary text.

Do not use teal, coral, or gold for body text unless the combination meets WCAG 2.2 AA contrast requirements.

## Typography

Use the frontend’s semantic font tokens and Tailwind typography utilities.

- **Font family:** `font-sans` backed by the system UI font stack.
- **Display:** `text-5xl sm:text-6xl font-extrabold tracking-wide`
- **Page title:** `text-3xl sm:text-4xl font-extrabold tracking-wide`
- **Section title:** `text-2xl sm:text-3xl font-extrabold`
- **Card title:** `text-xl font-bold`
- **Body:** `text-base`
- **Emphasized body:** `text-base font-medium`
- **Small:** `text-sm font-medium`
- **Metadata:** `text-xs font-medium`

Use display typography only for authentication screens, major empty states, onboarding, or important product moments.

Keep paragraph letter spacing normal. Wider letter spacing is reserved for short headings, labels, and decorative banners.

## Spacing

Use Tailwind’s standard spacing scale. The design follows an eight-pixel rhythm while permitting four-pixel adjustments for compact details.

| Role | Tailwind value | Approximate size |
| --- | --- | --- |
| Extra small | `2` | 8px |
| Small | `4` | 16px |
| Medium | `6` | 24px |
| Large | `8` | 32px |
| Extra large | `12` | 48px |

Prefer consistent combinations such as:

- `gap-4`
- `p-6`
- `space-y-6`
- `py-8`
- `px-4 sm:px-6 lg:px-8`

Use compact spacing for task metadata and larger spacing between major page sections.

## Border radius

- **Tags and compact controls:** `rounded-lg`
- **Inputs and ordinary buttons:** `rounded-xl`
- **Cards and panels:** `rounded-2xl`
- **Feature cards and dialogs:** `rounded-3xl`
- **Pills, badges, and avatars:** `rounded-full`

## Elevation and glow

Register recurring shadows as semantic Tailwind shadow tokens.

Recommended semantic shadows include:

- `shadow-subtle`: neutral low-opacity elevation for menus.
- `shadow-card`: soft teal-tinted elevation for cards.
- `shadow-coral-glow`: warning or urgent emphasis.
- `shadow-primary-glow`: active brand controls.
- `shadow-accent-glow`: important actions and milestones.
- `shadow-sky-glow`: assistant and informational emphasis.

Use glows sparingly. They should add tactile depth without reducing contrast or making the interface noisy.

Do not use heavy plain-black shadows on important interactive elements.

A visible focus ring is still required. A glow must never be the only keyboard-focus indicator.

## Layout and responsive behavior

- Build mobile-first with unprefixed Tailwind utilities.
- Enhance layouts through `sm`, `md`, `lg`, and larger responsive variants.
- Use a single-column layout on narrow screens.
- Add dashboard columns only when content remains readable.
- Keep major content inside a consistent centered maximum width.
- Prevent horizontal scrolling at approximately 375px viewport width.
- Keep interactive targets approximately 44px or larger.
- Do not use percentage heights for layout-critical elements.
- Do not make hover the only way to discover an action.

## Application identity

Use a StudyOps wordmark or study-themed visual mark.

The identity may reuse the retro layered-card pattern through abstract representations of:

- notebooks;
- flashcards;
- books;
- calendar blocks; or
- study-session cards.

Decorative branding may include:

- slightly rotated layered shapes;
- a cream banner with a dark outline;
- teal lettering with gold emphasis; and
- subtle offset shadows.

Do not reproduce Flip7 branding, its logo, game packaging, or its numeral treatment.

Keep the complete decorative treatment for authentication, onboarding, and major empty states. Use a simplified mark in navigation and dense dashboard screens.

## Buttons

Buttons use clear text labels, strong focus-visible treatment, and short responsive transitions.

### Primary action

Use a gold surface with dark readable text, `rounded-full` or `rounded-xl`, and a restrained accent glow.

### Secondary action

Use a teal surface or outlined teal treatment.

### Quiet action

Use a transparent or soft-primary treatment.

### Danger action

Use coral only for destructive or urgent actions.

### Icon action

Use a rounded-square control with at least a 44px interactive area and an accessible name.

Pressed states may use a slight scale reduction. Disable scale animation when reduced motion is preferred.

## Cards

Use a white or cream surface, `rounded-2xl`, a semantic card shadow, and an optional colored left accent border.

### Subject cards

Use teal as the default accent. A stable subject color may be used when that information exists in the product.

### Task cards

Use accent colors to reinforce priority or status. Always include a text label or icon so status is not communicated through color alone.

### Study-session cards

- Teal: scheduled
- Green: completed
- Coral or neutral: cancelled
- Gold: currently highlighted or requiring attention

### Error and conflict cards

Use coral emphasis with a clearly written explanation and an available recovery action.

## Dashboard summaries

A summary card should contain:

- one primary value;
- one short label;
- only the metadata needed to understand it; and
- an optional icon or status indicator.

Suitable summaries include:

- upcoming tasks;
- study minutes;
- completed sessions;
- active subjects;
- approaching deadlines; and
- planning conflicts.

Use playful colors and tactile elevation without turning study progress into a competitive ranking.

## Forms and inputs

- Use cream or white input surfaces with visible borders.
- Keep labels visible; placeholders do not replace labels.
- Use `rounded-xl` and comfortable vertical padding.
- Provide a strong `focus-visible` ring.
- Render field errors beside the relevant controls.
- Preserve backend field association when displaying validation errors.
- Use coral for errors and green for success, accompanied by text or an icon.

## Navigation

Use teal as the structural navigation color. Reserve gold for a high-value action or a small active indicator.

- Keep labels explicit.
- Clearly distinguish the current location.
- Provide distinct focus, hover, active, and pressed states.
- Use a compact mobile navigation pattern.
- Use a stable sidebar or header on desktop when appropriate.
- Do not hide essential navigation behind hover interactions.

## Schedule and calendar

- Use clean grid alignment and readable time labels.
- Use colored accents to distinguish subjects.
- Avoid large saturated backgrounds behind dense schedule text.
- Identify overlaps, conflicts, cancelled sessions, and unscheduled work using both text and visual treatment.
- Maintain contrast when several sessions appear together.
- Keep schedule controls usable on touch screens and with a keyboard.

## Assistant and schedule review

Use sky blue for informational assistant surfaces and teal for ordinary conversation structure.

Draft schedules should reuse the same task and session patterns used elsewhere in StudyOps.

- Gold emphasizes approval and the recommended next action.
- Coral emphasizes cancellation, conflicts, or destructive confirmation.
- Editing feedback uses a labeled form.
- Interrupted, completed, cancelled, loading, and error states must be visually distinct and identified in text.
- Do not call the assistant directly if the API contract says the browser cannot safely satisfy its authentication requirements.

## Section titles

Section headings may use:

- a small icon inside a separately aligned container;
- bold typography; and
- a subtle dashed divider.

Use a real icon or decorative element instead of depending on emoji text for alignment.

Hide decorative icons from assistive technology.

## Motion

- Keep ordinary hover, press, focus, and disclosure transitions at or below 300ms.
- Use gentle scale, lift, or glow changes for tactile feedback.
- Reserve celebration for meaningful moments such as completing a major study goal or approving a schedule.
- Do not run decorative animations indefinitely on ordinary dashboards.
- Respect `prefers-reduced-motion`.
- Provide an equivalent static state.
- Never make animation essential to understanding or completing a task.

## Do and don’t

1. Do use teal as the main structural brand color.
2. Do reserve gold for important actions, highlights, and milestones.
3. Do use coral deliberately for urgency, warnings, and destructive actions.
4. Do use cream for warm inputs and emphasized surfaces.
5. Do use colored shadows and glows sparingly.
6. Do use rounded cards, tactile controls, and occasional dashed dividers.
7. Do use left-border accents when they improve status scanning.
8. Do keep dense study information calm and readable.
9. Do implement styling with Tailwind utilities and semantic theme tokens.
10. Don’t place raw hexadecimal colors in JSX.
11. Don’t repeat arbitrary design values throughout components.
12. Don’t reproduce Flip7 names, controls, rankings, or game packaging.
13. Don’t use mini-program-only units or elements such as `rpx` or `view`.
14. Don’t communicate meaning using color, hover, or animation alone.
15. Don’t let decoration overpower deadlines, schedules, validation, or primary actions.