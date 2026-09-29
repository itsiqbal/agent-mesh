---
name: nextjs-react-conventions
description: Conventions for building Next.js (App Router) and React frontends — component structure, data fetching, state management, and styling. Use when creating or modifying frontend pages or components.
---
# Next.js / React Conventions

## Components
- Functional components with hooks only.
- Server Components by default (App Router); add `"use client"` only when you need interactivity, browser APIs, or state.
- Colocate a component, its styles, and its tests in the same folder.

## Data fetching
- Fetch data on the server (Server Components / Route Handlers) where possible; use React Query (TanStack Query) for client-side fetching/caching when interactivity requires it.
- Never call internal service secrets or private APIs from client components — proxy through a Route Handler.

## State
- Local component state with `useState`/`useReducer`; cross-component state with React Context or Zustand — avoid introducing a heavier state library unless the app genuinely needs it.

## Styling
- Tailwind CSS utility classes; extract a component when a class list gets unwieldy rather than reaching for custom CSS files.

## Forms
- `react-hook-form` + a zod resolver for validation; surface field-level errors, not just a generic failure message.

## Testing
- Unit/interaction tests with React Testing Library (test behavior, not implementation details).
- Critical user flows covered by Playwright end-to-end tests.

## Accessibility
- Semantic HTML first; label every form control; verify keyboard navigation and focus order on interactive components.
