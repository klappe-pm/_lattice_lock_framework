import json
import logging
from typing import Set
from aiohttp import web, WSMsgType

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[web.WebSocketResponse] = set()

    async def handle_connection(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.active_connections.add(ws)
        logger.info("New WebSocket connection")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    if msg.data == 'ping':
                        await ws.send_str('pong')
                elif msg.type == WSMsgType.ERROR:
                    logger.error('ws connection closed with exception %s', ws.exception())
        finally:
            self.active_connections.remove(ws)
            logger.info("WebSocket connection closed")

        return ws

    async def broadcast(self, message: dict):
        """Broadcast a message to all active connections."""
        if not self.active_connections:
            return

        data = json.dumps(message)
        # Create a list of tasks to send messages concurrently? 
        # Or just iterate. Iterating is safer for now to avoid race conditions on the set.
        # We iterate over a copy or just handle exceptions.
        
        to_remove = set()
        for ws in self.active_connections:
            try:
                await ws.send_str(data)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                to_remove.add(ws)
        
        self.active_connections -= to_remove
