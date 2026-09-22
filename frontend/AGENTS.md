# StudyOps Frontend Instructions

These instructions apply to all work inside `frontend/`. They extend the repository-level `AGENTS.md`; follow both files, and use this file for frontend-specific decisions. Do not weaken the repository rules for scope, dependencies, API contracts, authentication, or verification.

## 1. Frontend Baseline

- Use React 19, TypeScript in strict mode, React Router 8, Tailwind CSS 4, Vite 8, and Oxlint.
- Use npm and keep `package.json` and `package-lock.json` synchronized.
- Prefer the existing dependencies, React APIs, browser APIs, and ordinary CSS. Obtain confirmation before adding a production dependency or substantial development dependency.
- Preserve unrelated and user-authored changes. Do not rewrite working frontend code merely to make it match a preferred pattern.

## 2. Folder Organization

Organize code by screen domain, with shared components and domain types kept separate:

```text
src/
|-- components/
|   |-- Button.tsx
|   `-- SubjectCard.tsx
|-- screens/
|   `-- subjects/
|       |-- SubjectsPage.tsx
|       |-- loaders.ts
|       |-- actions.ts
|       |-- hooks.ts
|       `-- helpers.ts
|-- types/
|   |-- subjects.ts
|   `-- user.ts
`-- router.tsx
```

### Screen domains

- Create every product area under `src/screens/<domain>/`. Examples include `auth`, `subjects`, `tasks`, `sessions`, `preferences`, and `assistant`.
- Use lowercase kebab-case when a domain name contains more than one word, such as `study-sessions`.
- Keep the domain's route pages, loaders, actions, screen-specific hooks, and helpers inside that domain folder. For example, subject hooks belong in `src/screens/subjects/hooks.ts`.
- Use `loaders.ts` for React Router loader functions, `actions.ts` for React Router action functions, `hooks.ts` for hooks owned by that screen domain, and `helpers.ts` for pure domain-specific helpers. Create only the files the screen actually needs; do not add empty placeholders.
- Route pages are the only React components that belong in a screen-domain folder. Name them with a `Page` suffix, such as `SubjectsPage.tsx`.
- Keep page components focused on route orchestration and page composition. Extract reusable or substantial presentation pieces into `src/components/`.

### Shared components, hooks, and utilities

- Keep reusable React components in the flat `src/components/` directory. Do not create domain, UI, or layout subdirectories beneath it unless these instructions are deliberately revised.
- Do not put reusable React components in `src/screens/`. A component used by only one page may remain inline in that page while it is small; once extracted, place it in `src/components/`.
- Move a hook to `src/hooks/` only when it is genuinely shared across screen domains. Otherwise keep it in the owning domain's `hooks.ts`.
- Shared low-level request, authentication, parsing, or formatting utilities may live in `src/lib/`. Endpoint-specific request logic remains in the owning screen domain's loader or action.
- Avoid barrel files by default. Import directly from the defining module unless a folder develops a deliberate, stable public interface.

### Types and naming

- Keep domain model, API payload, and API response types in `src/types/<domain>.ts`, such as `src/types/subjects.ts`. Reuse these types instead of duplicating shapes inside components or screens.
- Keep component filenames and component names in PascalCase. Use named exports, for example `export function SubjectCard(...)`.
- Name component props `<ComponentName>Props` and type props explicitly. Do not use `React.FC` merely to provide the component type.
- Prefix custom hooks with `use`. Name event handlers `handle<Action>` and callback props `on<Action>`.
- Use `import type` for type-only imports. Use relative imports until the project intentionally configures and documents an import alias.

## 3. Routing and Data Flow

- Keep the complete route tree centralized in `src/router.tsx`. Screen modules may export route pages, loaders, and actions, but must not create independent routers.
- Use lowercase kebab-case URL segments. Use nested routes and layout routes when several screens share navigation or page structure.
- Use React Router navigation APIs for internal navigation rather than ordinary document links.
- Prefer route loaders for data needed to render a route. Read loader results through React Router rather than copying server data into component state.
- Prefer route actions, `<Form>`, or fetchers for mutations. Use navigation and fetcher state to render pending and disabled states and to prevent accidental duplicate submissions.
- Reserve direct component-level requests for interactions that do not fit route navigation, such as assistant chat, polling, autocomplete, or intentionally deferred live data.
- Keep endpoint-specific API calls in the owning domain's `loaders.ts` or `actions.ts`. Factor out only genuinely shared transport behavior.
- Represent expected request failures through the route's error handling and provide useful page-level or control-level recovery. Never silently swallow an error.

## 4. State Management

- Use component state for local, ephemeral UI state.
- Use URL path parameters and search parameters for shareable or restorable state such as filters, searches, pagination, and selected views.
- Use React Router loader data for server-backed route state; do not duplicate it into Context or local state without a specific editing or synchronization need.
- Use Context only for truly application-wide concerns such as the authenticated user or a future approved theme. Keep contexts narrowly scoped and expose a typed custom hook.
- Do not add Redux, Zustand, a server-state library, or another state-management dependency without explicit approval.

## 5. API and Authentication

- Inspect the Django views, serializers, URLs, filters, and tests before integrating an endpoint. Do not invent request or response fields.
- Build API URLs from `VITE_API_BASE_URL`; never hardcode a local or deployment host in source code.
- Preserve cookie-based authentication and include credentials when required by the established API contract.
- Never read authentication cookies from client code or store access or refresh tokens in local storage, session storage, application state, logs, fixtures, screenshots, or user-visible errors.
- Model loading, empty, validation-error, server-error, success, disabled, and retry states where they apply.
- Keep temporary mock data behind an explicit boundary, label it as temporary, and report the backend contract gap.

## 6. Component Conventions

- Prefer small function components with explicit inputs and named exports.
- Keep data loading and mutation orchestration in pages, loaders, actions, and domain hooks. Keep reusable components driven by props and callbacks.
- Prefer composition over large components with many boolean mode props.
- Use stable domain identifiers as React keys; do not use array indexes when items can be inserted, removed, or reordered.
- Avoid effects for values that can be derived during render. Use effects only to synchronize with an external system and clean them up correctly.
- Do not suppress TypeScript or lint errors without documenting the concrete reason next to the suppression.

## 7. Styling and Design Tokens

- Use Tailwind utility classes as the default styling approach for components and pages.
- Limit global CSS to the Tailwind import, resets, semantic design tokens, typography defaults, and behavior that is genuinely shared across the application.
- Do not create component CSS files or CSS modules for ordinary styling. If Tailwind cannot reasonably express a required behavior, keep the smallest justified CSS rule in the appropriate shared stylesheet and explain the exception.
- Keep repeated product colors, typography, spacing, radii, and shadows behind semantic tokens. Avoid repeating arbitrary values or raw brand colors throughout JSX.
- In long class lists, group utilities in this order: layout and positioning, sizing, spacing, typography, color and border, effects, then interaction and responsive variants.

### Current tokens

`src/index.css` currently defines `--text`, `--text-h`, `--bg`, `--border`, `--code-bg`, `--accent`, `--accent-bg`, `--accent-border`, `--social-bg`, `--shadow`, `--sans`, `--heading`, and `--mono`.

These are Vite starter values, not an approved StudyOps design system. Reuse them only while existing starter UI depends on them. When implementing the product design, replace or extend them deliberately with semantic tokens rather than treating their names or values as permanent. The existing operating-system dark-mode rules are likewise provisional and do not establish a final theming requirement.

## 8. Responsive Design

- Build mobile-first: unprefixed utilities define the narrow-screen experience and larger breakpoints enhance it.
- Use Tailwind's default breakpoints consistently:
  - `sm`: 640px and wider
  - `md`: 768px and wider
  - `lg`: 1024px and wider
  - `xl`: 1280px and wider
  - `2xl`: 1536px and wider
- Add a custom breakpoint only when a real layout requirement cannot be handled by the defaults, and document why it is needed.
- Prevent horizontal overflow, preserve readable line lengths, and ensure controls remain usable without hover at touch widths.

## 9. Accessibility

Target WCAG 2.2 AA for all new and changed UI.

- Use semantic HTML and native controls before ARIA-based substitutes.
- Ensure every interaction works with a keyboard and has a clearly visible focus indicator.
- Give every form control an accessible name. Associate help text and validation errors programmatically, and move or announce focus appropriately after failed submissions.
- Maintain sufficient text and non-text contrast in every supported visual state.
- Use headings in a logical order, descriptive link and button text, and meaningful document titles.
- Give informative images useful alternative text and decorative images an empty `alt`; hide decorative SVGs from assistive technology.
- Announce important asynchronous status changes with an appropriate live region without creating noisy repeated announcements.
- Respect `prefers-reduced-motion` and do not make animation essential to understanding or operating the interface.
- Make interactive targets sufficiently large and do not rely on color, hover, or pointer input alone to convey meaning.

## 10. Verification

For every frontend behavior change, run these commands from `frontend/`:

```text
npm run lint
npm run build
```

Then verify the affected UI in a browser:

1. Check a narrow mobile viewport, approximately 375px wide, and a desktop viewport, approximately 1440px wide. Check intermediate breakpoints when the layout changes there.
2. Exercise the primary interaction path and relevant loading, empty, validation, error, disabled, success, hover, and focus states.
3. Test keyboard navigation, focus order, labels, error announcements, contrast, and obvious overflow.
4. Inspect the browser console for errors and warnings.

The frontend currently has no automated test command or configured test runner. Do not claim that automated frontend tests passed. If a test runner is added later with approval, update these instructions and `package.json` together.

For a documentation-only change such as editing this file, verify the instructions against the repository-level `AGENTS.md` and current frontend configuration. Do not run lint or build unless application or configuration files also changed.
