# Frontend Migration Status

The dashboard frontend is being migrated from Vanilla JS to React + Vite.

## Current Status
- **Old Frontend**: `src/lattice_lock/dashboard/frontend` (Active)
- **New Frontend**: `src/lattice_lock/dashboard/ui` (In Development)

## Next Steps to Finalize
1. Navigate to `src/lattice_lock/dashboard/ui`
2. Run `npm install`
3. Run `npm run dev` to test locally (proxies to backend on 8080)
4. Port remaining components from `old/components/*.js` to React components in `src/components`
5. Run `npm run build` -> output goes to `../static` (replacing old frontend logic)
6. Update `src/lattice_lock/dashboard/backend.py` to serve from `static/` if not already.

## Why Migrate?
- Better state management for real-time WebSocket data
- Component isolation for charts
- Tailwind CSS for maintainable styling
