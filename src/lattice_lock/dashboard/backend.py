import asyncio
from aiohttp import web
import json
from .aggregator import DataAggregator
from .websocket import WebSocketManager

class DashboardBackend:
    def __init__(self):
        self.aggregator = DataAggregator()
        self.ws_manager = WebSocketManager()
        self.app = web.Application()
        self.setup_routes()
        self.app.on_startup.append(self.start_background_tasks)

    def setup_routes(self):
        self.app.router.add_get('/dashboard/summary', self.handle_summary)
        self.app.router.add_get('/dashboard/projects', self.handle_projects)
        self.app.router.add_get('/dashboard/metrics', self.handle_metrics)
        self.app.router.add_get('/dashboard/live', self.ws_manager.handle_connection)

    async def handle_summary(self, request):
        data = self.aggregator.get_project_summary()
        return web.json_response(data)

    async def handle_projects(self, request):
        data = self.aggregator.get_all_projects()
        return web.json_response(data)

    async def handle_metrics(self, request):
        snapshot = self.aggregator.get_metrics()
        # Convert dataclass to dict
        data = {
            "total_validations": snapshot.total_validations,
            "success_rate": snapshot.success_rate,
            "avg_response_time": snapshot.avg_response_time,
            "error_counts": snapshot.error_counts,
            "health_score": snapshot.health_score,
            "timestamp": snapshot.timestamp
        }
        return web.json_response(data)

    async def start_background_tasks(self, app):
        app['mock_updater'] = asyncio.create_task(self.mock_data_updater())

    async def mock_data_updater(self):
        """Simulate real-time updates for demonstration."""
        import random
        projects = ["proj-alpha", "proj-beta", "proj-gamma"]
        statuses = ["healthy", "valid", "error", "warning"]
        
        while True:
            await asyncio.sleep(5)
            # Pick a random project and update it
            pid = random.choice(projects)
            status = random.choice(statuses)
            
            self.aggregator.update_project_status(pid, status)
            
            # Broadcast update
            update_msg = {
                "type": "project_update",
                "project_id": pid,
                "status": status,
                "metrics": self.aggregator.get_project_summary()
            }
            await self.ws_manager.broadcast(update_msg)

def create_app():
    backend = DashboardBackend()
    return backend.app

if __name__ == '__main__':
    web.run_app(create_app(), port=8080)
