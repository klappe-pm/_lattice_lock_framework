# Prompt 3.4.2 - Dashboard Frontend

**Tool:** Codex CLI
**Epic:** 3.4 - Admin Dashboard
**Phase:** 3 - Error Handling & Admin

## Context

The Admin Dashboard needs a frontend that displays project status, metrics, and alerts in a user-friendly interface. The frontend should connect to the dashboard backend and display real-time updates.

## Goal

Implement the dashboard frontend with real-time status display and interactive controls.

## Steps

1. Create `src/lattice_lock/dashboard/frontend/` directory:
   ```
   frontend/
   ├── index.html
   ├── styles.css
   ├── app.js
   └── components/
       ├── project-card.js
       ├── metrics-chart.js
       └── alert-list.js
   ```

2. Create `index.html`:
   - Dashboard layout with header, sidebar, main content
   - Project list section
   - Metrics visualization section
   - Alerts/errors section
   - Real-time status indicators

3. Create `app.js`:
   - WebSocket connection to backend
   - State management for projects and metrics
   - Event handlers for user interactions
   - Auto-refresh logic

4. Create components:
   - `project-card.js`: Display project status with health indicator
   - `metrics-chart.js`: Chart.js visualization for metrics
   - `alert-list.js`: Scrollable list of recent alerts

5. Implement real-time updates:
   - WebSocket message handling
   - DOM updates on status change
   - Visual indicators for changes (flash, highlight)

6. Add interactive controls:
   - Trigger rollback button
   - Refresh data button
   - Filter by project/status
   - Time range selector for metrics

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Dashboard displays all project statuses
- Real-time updates work correctly
- Metrics visualizations are accurate
- Interactive controls function properly

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use vanilla JS or lightweight framework
- Keep dependencies minimal
- Ensure responsive design
