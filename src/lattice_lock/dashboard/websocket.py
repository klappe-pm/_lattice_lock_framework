"""
Lattice Lock Dashboard WebSocket Manager

Provides real-time updates to connected dashboard clients via WebSocket.
Supports event broadcasting, connection management, and heartbeat/keepalive.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""

    websocket: WebSocket
    connected_at: float
    last_activity: float
    client_id: Optional[str] = None


class WebSocketManager:
    """
    Manages WebSocket connections for real-time dashboard updates.

    Features:
    - Event broadcasting to all connected clients
    - Connection lifecycle management
    - Heartbeat/keepalive support
    - Automatic cleanup of dead connections
    """

    # Heartbeat interval in seconds
    HEARTBEAT_INTERVAL = 30
    # Connection timeout in seconds (no activity)
    CONNECTION_TIMEOUT = 120

    def __init__(self):
        """Initialize the WebSocket manager."""
        self._connections: dict[int, ConnectionInfo] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False

    @property
    def active_connections(self) -> list[WebSocket]:
        """Get list of active WebSocket connections."""
        return [info.websocket for info in self._connections.values()]

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> None:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept
            client_id: Optional client identifier
        """
        await websocket.accept()

        conn_id = id(websocket)
        current_time = time.time()

        self._connections[conn_id] = ConnectionInfo(
            websocket=websocket,
            connected_at=current_time,
            last_activity=current_time,
            client_id=client_id,
        )

        logger.info(
            "WebSocket connection established: %s (client=%s, total=%d)",
            conn_id,
            client_id or "anonymous",
            self.connection_count,
        )

        # Send welcome message
        await self._send_to_connection(
            websocket,
            {
                "type": "connected",
                "message": "Connected to Lattice Lock Dashboard",
                "timestamp": current_time,
            },
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
        """
        conn_id = id(websocket)
        if conn_id in self._connections:
            info = self._connections.pop(conn_id)
            logger.info(
                "WebSocket disconnected: %s (client=%s, duration=%.1fs, remaining=%d)",
                conn_id,
                info.client_id or "anonymous",
                time.time() - info.connected_at,
                self.connection_count,
            )

    async def handle_connection(self, websocket: WebSocket) -> None:
        """
        Handle a WebSocket connection lifecycle.

        This method accepts the connection, processes messages,
        and handles disconnection automatically.

        Args:
            websocket: The WebSocket connection to handle
        """
        await self.connect(websocket)

        try:
            while True:
                try:
                    # Wait for messages with a timeout
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=self.HEARTBEAT_INTERVAL,
                    )

                    # Update activity timestamp
                    conn_id = id(websocket)
                    if conn_id in self._connections:
                        self._connections[conn_id].last_activity = time.time()

                    # Handle message
                    await self._handle_message(websocket, data)

                except asyncio.TimeoutError:
                    # Send heartbeat on timeout
                    await self._send_heartbeat(websocket)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error("WebSocket error: %s", e)
        finally:
            self.disconnect(websocket)

    async def _handle_message(self, websocket: WebSocket, data: str) -> None:
        """
        Handle an incoming WebSocket message.

        Supports:
        - ping: Responds with pong
        - subscribe: Subscribe to specific event types (future)
        - unsubscribe: Unsubscribe from event types (future)

        Args:
            websocket: The WebSocket connection
            data: The received message data
        """
        try:
            # Handle simple ping
            if data == "ping":
                await websocket.send_text("pong")
                return

            # Try to parse as JSON
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                # Not JSON, just echo back
                await websocket.send_text(data)
                return

            msg_type = message.get("type", "")

            if msg_type == "ping":
                await self._send_to_connection(
                    websocket,
                    {"type": "pong", "timestamp": time.time()},
                )
            elif msg_type == "subscribe":
                # Future: Handle subscription to specific event types
                await self._send_to_connection(
                    websocket,
                    {"type": "subscribed", "topics": message.get("topics", [])},
                )
            else:
                # Unknown message type, acknowledge receipt
                await self._send_to_connection(
                    websocket,
                    {"type": "ack", "received": msg_type},
                )

        except Exception as e:
            logger.error("Error handling message: %s", e)
            await self._send_to_connection(
                websocket,
                {"type": "error", "message": str(e)},
            )

    async def _send_heartbeat(self, websocket: WebSocket) -> None:
        """Send heartbeat to a connection."""
        try:
            await self._send_to_connection(
                websocket,
                {"type": "heartbeat", "timestamp": time.time()},
            )
        except Exception as e:
            logger.debug("Heartbeat failed for connection: %s", e)

    async def _send_to_connection(
        self,
        websocket: WebSocket,
        message: dict[str, Any],
    ) -> bool:
        """
        Send a message to a specific connection.

        Args:
            websocket: Target WebSocket connection
            message: Message dictionary to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error("Failed to send to WebSocket: %s", e)
            return False

    async def broadcast(self, message: dict[str, Any]) -> int:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message dictionary to broadcast

        Returns:
            Number of clients that received the message
        """
        if not self._connections:
            return 0

        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = time.time()

        sent_count = 0
        dead_connections: list[int] = []

        for conn_id, info in list(self._connections.items()):
            try:
                await info.websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning("Failed to broadcast to %s: %s", conn_id, e)
                dead_connections.append(conn_id)

        # Clean up dead connections
        for conn_id in dead_connections:
            if conn_id in self._connections:
                del self._connections[conn_id]

        if dead_connections:
            logger.info(
                "Removed %d dead connections during broadcast",
                len(dead_connections),
            )

        return sent_count

    async def broadcast_event(
        self,
        event_type: str,
        data: dict[str, Any],
        project_id: Optional[str] = None,
    ) -> int:
        """
        Broadcast a typed event to all clients.

        Args:
            event_type: Type of event (e.g., "project_update", "metrics_update")
            data: Event data
            project_id: Optional project ID this event relates to

        Returns:
            Number of clients that received the event
        """
        message = {
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
        }

        if project_id:
            message["project_id"] = project_id

        return await self.broadcast(message)

    async def send_to_client(
        self,
        client_id: str,
        message: dict[str, Any],
    ) -> bool:
        """
        Send a message to a specific client by ID.

        Args:
            client_id: Client identifier
            message: Message to send

        Returns:
            True if sent, False if client not found or send failed
        """
        for info in self._connections.values():
            if info.client_id == client_id:
                return await self._send_to_connection(info.websocket, message)

        logger.warning("Client not found: %s", client_id)
        return False

    def get_connection_stats(self) -> dict[str, Any]:
        """
        Get statistics about current connections.

        Returns:
            Dictionary with connection statistics
        """
        current_time = time.time()
        return {
            "total_connections": self.connection_count,
            "connections": [
                {
                    "client_id": info.client_id,
                    "connected_duration": current_time - info.connected_at,
                    "last_activity": current_time - info.last_activity,
                }
                for info in self._connections.values()
            ],
        }

    async def close_all(self) -> None:
        """Close all active WebSocket connections."""
        for info in list(self._connections.values()):
            try:
                await info.websocket.close()
            except Exception:
                pass

        self._connections.clear()
        logger.info("All WebSocket connections closed")
