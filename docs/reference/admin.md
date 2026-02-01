---
title: admin
type: guide
status: stable
categories: [reference, admin]
sub_categories: [dashboard]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [ref-admin-001]
tags: [admin, dashboard, monitoring, guide]
---

# Lattice Lock Admin Dashboard Guide

The Lattice Lock Admin Dashboard provides a real-time monitor for your projects, health status, and rollback operations.

## Starting the Dashboard

The dashboard is integrated into the `lattice-lock` CLI.

```bash
# Start the admin server on the default port (8080)
lattice-lock admin serve

# Start on a custom port
lattice-lock admin serve --port 9000

# Enable debug mode and auto-reload (for development)
lattice-lock admin serve --reload --debug
```

Once running, the API is accessible at `http://127.0.0.1:8080`.

## Features

### 1. Project Management
- **List Projects**: View all registered projects and their active status.
- **Register Project**: Add new projects to the monitoring system.

### 2. Health Monitoring
- **Validation Status**: Real-time view of Schema, Sheriff, and Gauntlet validation states (Passed/Failed/Pending).
- **Error Tracking**: Aggregated view of recent errors, categorized by severity (Critical, High, Medium, Low).

### 3. Rollback Operations
- **Checkpoints**: View available rollback points (auto-generated during significant events).
- **Trigger Rollback**: Restore a project to a previous state directly from the API.

## API Documentation

The Admin server comes with built-in interactive documentation.
- **Swagger UI**: Visit `http://127.0.0.1:8080/docs`
- **ReDoc**: Visit `http://127.0.0.1:8080/redoc`

## Security Note

By default, the Admin API binds to `127.0.0.1` and does not require authentication. For production deployments, ensure it is deployed behind a secure reverse proxy (e.g., Nginx, AWS ALB) with appropriate authentication headers.
