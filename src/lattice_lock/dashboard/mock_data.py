import asyncio
import random

from .aggregator import DataAggregator
from .websocket import WebSocketManager


async def mock_data_updater(aggregator: DataAggregator, ws_manager: WebSocketManager) -> None:
    """
    Simulate real-time updates for demonstration.

    This background task periodically updates project statuses
    and broadcasts changes to connected WebSocket clients.
    """
    projects = ["proj-alpha", "proj-beta", "proj-gamma"]
    statuses = ["healthy", "valid", "error", "warning"]

    # Initialize demo projects
    for pid in projects:
        aggregator.register_project(pid, name=f"Demo Project {pid.split('-')[1].title()}")

    while True:
        await asyncio.sleep(5)

        # Pick a random project and update it
        pid = random.choice(projects)
        new_status = random.choice(statuses)

        project = aggregator.update_project_status(pid, new_status)

        # Broadcast update
        await ws_manager.broadcast_event(
            event_type="project_update",
            data={
                "project_id": pid,
                "status": new_status,
                "health_score": project.health_score,
                "summary": aggregator.get_project_summary().to_dict(),
            },
            project_id=pid,
        )
