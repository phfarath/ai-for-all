# AI Learning Platform Frontend

This directory contains the React Progressive Web App (PWA) for the AI Learning Platform.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast build and dev experience
- **React Router** for SPA routing
- **Zustand** for state management (not yet used)
- **Supabase JS client** for auth and data access
- **Vite PWA plugin** for offline-ready PWA features

## Features (Planned)

- Student dashboard with enrollment and progress tracking
- LLM tutor widget with token quota management
- Interactive video player with inline quizzes and bookmarks
- Code labs powered by Pyodide (Python in browser)
- No-code ML pipeline builder (WASM + sklearn)
- Course editor with rich text and quiz builder
- Media uploader and asset manager
- Search and recommendations
- Instructor panel with basic analytics

## Getting Started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Copy the example environment file and configure:

   ```bash
   cp .env.example .env
   # Edit .env with your Supabase and API URLs
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Build for production:

   ```bash
   npm run build
   ```

## Environment Variables

- `VITE_SUPABASE_URL`: Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Your Supabase anon/public key
- `VITE_API_BASE_URL`: FastAPI backend base URL (default: `http://localhost:8000`)

## Project Structure

```
src/
├── pages/          # Page-level components
├── components/     # Reusable UI components (to be added)
├── lib/            # Client libraries (Supabase, API)
├── store/          # Zustand stores (to be added)
├── pwa/            # PWA-specific code (service worker, etc)
├── styles.css      # Global styles
├── App.tsx         # Main app component
└── main.tsx        # React entry point
```

## PWA Features

This app is configured as a PWA with:

- Offline support via service worker
- Installable on mobile and desktop
- Manifest for app metadata

The PWA configuration is in `vite.config.ts` using the `vite-plugin-pwa` plugin.

## Current Status

This is the initial scaffolding. Future work includes:

- Authentication flow with Supabase Auth
- Dashboard with learner profile
- Course and lesson browsing
- Interactive content players
- Offline-first capabilities with IndexedDB
