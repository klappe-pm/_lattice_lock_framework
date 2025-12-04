"""
WebSocket Manager for Dashboard Backend

Provides WebSocket endpoint for real-time updates, event broadcasting
for status changes, connection management, and heartbeat/keepalive.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from weakref import WeakSet


class EventType(str, Enum):
    """Types of events that can be broadcast."""
    VALIDATION_COMPLETE = "validation_complete"
    PROJECT_STATUS_CHANGED = "project_status_changed"
    HEALTH_UPDATED = "health_updated"
    ERROR_DETECTED = "error_detected"
    METRICS_UPDATED = "metrics_updated"
    HEARTBEAT = "heartbeat"
    CONNECTION_ESTABLISHED = "connection_established"


@dataclass
class WebSocketMessage:
    """Message structure for WebSocket communication."""
    event_type: EventType
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_json(self) -> str:
        """Convert to JSON string for transmission."""
        return json.dumps({
            "event": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "WebSocketMessage":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(
            event_type=EventType(data["event"]),
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting.
    
    Handles connection lifecycle, heartbeat/keepalive, and
    efficient message distribution to connected clients.
    """
    
    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        connection_timeout: float = 120.0,
    ):
        """Initialize the connection manager.
        
        Args:
            heartbeat_interval: Seconds between heartbeat messages
            connection_timeout: Seconds before considering a connection dead
        """
        self._connections: dict[str, Any] = {}  # connection_id -> websocket
        self._connection_metadata: dict[str, dict[str, Any]] = {}
        self._heartbeat_interval = heartbeat_interval
        self._connection_timeout = connection_timeout
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._running = False
        self._event_handlers: dict[EventType, list[Callable[..., Any]]] = {}
    
    async def start(self) -> None:
        """Start the connection manager and heartbeat task."""
        if self._running:
            return
        
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def stop(self) -> None:
        """Stop the connection manager and cleanup."""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for conn_id in list(self._connections.keys()):
            await self.disconnect(conn_id)
    
    async def connect(
        self,
        connection_id: str,
        websocket: Any,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a new WebSocket connection.
        
        Args:
            connection_id: Unique identifier for the connection
            websocket: The WebSocket connection object
            metadata: Optional metadata about the connection
        """
        self._connections[connection_id] = websocket
        self._connection_metadata[connection_id] = {
            "connected_at": datetime.utcnow(),
            "last_activity": time.time(),
            "message_count": 0,
            **(metadata or {}),
        }
        
        # Send connection established message
        await self.send_to(
            connection_id,
            WebSocketMessage(
                event_type=EventType.CONNECTION_ESTABLISHED,
                data={
                    "connection_id": connection_id,
                    "heartbeat_interval": self._heartbeat_interval,
                },
            ),
        )
    
    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection.
        
        Args:
            connection_id: The connection to remove
        """
        if connection_id in self._connections:
            websocket = self._connections.pop(connection_id)
            self._connection_metadata.pop(connection_id, None)
            
            try:
                await websocket.close()
            except Exception:
                pass  # Connection may already be closed
    
    async def send_to(
        self,
        connection_id: str,
        message: WebSocketMessage,
    ) -> bool:
        """Send a message to a specific connection.
        
        Args:
            connection_id: Target connection
            message: Message to send
        
        Returns:
            True if message was sent successfully
        """
        if connection_id not in self._connections:
            return False
        
        websocket = self._connections[connection_id]
        
        try:
            await websocket.send_text(message.to_json())
            
            if connection_id in self._connection_metadata:
                self._connection_metadata[connection_id]["last_activity"] = time.time()
                self._connection_metadata[connection_id]["message_count"] += 1
            
            return True
        except Exception:
            # Connection failed, remove it
            await self.disconnect(connection_id)
            return False
    
    async def broadcast(
        self,
        message: WebSocketMessage,
        exclude: Optional[set[str]] = None,
    ) -> int:
        """Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast
            exclude: Set of connection IDs to exclude
        
        Returns:
            Number of clients that received the message
        """
        exclude = exclude or set()
        sent_count = 0
        
        # Create list of connection IDs to avoid modification during iteration
        connection_ids = list(self._connections.keys())
        
        for conn_id in connection_ids:
            if conn_id not in exclude:
                if await self.send_to(conn_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeat messages to all connections."""
        while self._running:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                
                if not self._running:
                    break
                
                # Send heartbeat to all connections
                heartbeat = WebSocketMessage(
                    event_type=EventType.HEARTBEAT,
                    data={"server_time": datetime.utcnow().isoformat()},
                )
                
                await self.broadcast(heartbeat)
                
                # Check for timed out connections
                await self._cleanup_stale_connections()
                
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error but continue heartbeat loop
                pass
    
    async def _cleanup_stale_connections(self) -> None:
        """Remove connections that haven't responded recently."""
        now = time.time()
        stale_connections = []
        
        for conn_id, metadata in self._connection_metadata.items():
            last_activity = metadata.get("last_activity", 0)
            if now - last_activity > self._connection_timeout:
                stale_connections.append(conn_id)
        
        for conn_id in stale_connections:
            await self.disconnect(conn_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)
    
    def get_connection_info(self) -> list[dict[str, Any]]:
        """Get information about all active connections."""
        info = []
        for conn_id, metadata in self._connection_metadata.items():
            info.append({
                "connection_id": conn_id,
                "connected_at": metadata["connected_at"].isoformat(),
                "message_count": metadata["message_count"],
                "idle_seconds": time.time() - metadata["last_activity"],
            })
        return info
    
    def on_event(self, event_type: EventType) -> Callable[..., Any]:
        """Decorator to register an event handler.
        
        Args:
            event_type: The event type to handle
        
        Returns:
            Decorator function
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(func)
            return func
        return decorator
    
    async def handle_message(
        self,
        connection_id: str,
        message: WebSocketMessage,
    ) -> None:
        """Handle an incoming message from a client.
        
        Args:
            connection_id: Source connection
            message: Received message
        """
        if connection_id in self._connection_metadata:
            self._connection_metadata[connection_id]["last_activity"] = time.time()
        
        handlers = self._event_handlers.get(message.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(connection_id, message)
                else:
                    handler(connection_id, message)
            except Exception:
                pass  # Log error but continue processing


class WebSocketManager:
    """High-level WebSocket manager for the dashboard.
    
    Provides a simplified interface for broadcasting dashboard events
    and managing real-time updates.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self._connection_manager = ConnectionManager()
        self._subscribers: dict[str, set[str]] = {}  # topic -> connection_ids
    
    @property
    def connection_manager(self) -> ConnectionManager:
        """Get the underlying connection manager."""
        return self._connection_manager
    
    async def start(self) -> None:
        """Start the WebSocket manager."""
        await self._connection_manager.start()
    
    async def stop(self) -> None:
        """Stop the WebSocket manager."""
        await self._connection_manager.stop()
    
    async def connect(
        self,
        connection_id: str,
        websocket: Any,
        topics: Optional[list[str]] = None,
    ) -> None:
        """Connect a client and subscribe to topics.
        
        Args:
            connection_id: Unique connection identifier
            websocket: WebSocket connection object
            topics: List of topics to subscribe to
        """
        await self._connection_manager.connect(
            connection_id,
            websocket,
            metadata={"topics": topics or []},
        )
        
        for topic in (topics or []):
            if topic not in self._subscribers:
                self._subscribers[topic] = set()
            self._subscribers[topic].add(connection_id)
    
    async def disconnect(self, connection_id: str) -> None:
        """Disconnect a client and unsubscribe from all topics.
        
        Args:
            connection_id: Connection to disconnect
        """
        # Remove from all topic subscriptions
        for topic_subscribers in self._subscribers.values():
            topic_subscribers.discard(connection_id)
        
        await self._connection_manager.disconnect(connection_id)
    
    async def subscribe(self, connection_id: str, topic: str) -> None:
        """Subscribe a connection to a topic.
        
        Args:
            connection_id: Connection to subscribe
            topic: Topic to subscribe to
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(connection_id)
    
    async def unsubscribe(self, connection_id: str, topic: str) -> None:
        """Unsubscribe a connection from a topic.
        
        Args:
            connection_id: Connection to unsubscribe
            topic: Topic to unsubscribe from
        """
        if topic in self._subscribers:
            self._subscribers[topic].discard(connection_id)
    
    async def broadcast_validation_complete(
        self,
        project_id: str,
        passed: bool,
        error_count: int,
        warning_count: int,
        duration_ms: float,
    ) -> int:
        """Broadcast a validation completion event.
        
        Args:
            project_id: Project that was validated
            passed: Whether validation passed
            error_count: Number of errors
            warning_count: Number of warnings
            duration_ms: Validation duration
        
        Returns:
            Number of clients notified
        """
        message = WebSocketMessage(
            event_type=EventType.VALIDATION_COMPLETE,
            data={
                "project_id": project_id,
                "passed": passed,
                "error_count": error_count,
                "warning_count": warning_count,
                "duration_ms": duration_ms,
            },
        )
        return await self._connection_manager.broadcast(message)
    
    async def broadcast_project_status_changed(
        self,
        project_id: str,
        old_status: str,
        new_status: str,
        health_score: float,
    ) -> int:
        """Broadcast a project status change event.
        
        Args:
            project_id: Project that changed
            old_status: Previous status
            new_status: New status
            health_score: Current health score
        
        Returns:
            Number of clients notified
        """
        message = WebSocketMessage(
            event_type=EventType.PROJECT_STATUS_CHANGED,
            data={
                "project_id": project_id,
                "old_status": old_status,
                "new_status": new_status,
                "health_score": health_score,
            },
        )
        return await self._connection_manager.broadcast(message)
    
    async def broadcast_health_updated(
        self,
        overall_health: float,
        healthy_count: int,
        warning_count: int,
        critical_count: int,
    ) -> int:
        """Broadcast a health update event.
        
        Args:
            overall_health: Overall system health score
            healthy_count: Number of healthy projects
            warning_count: Number of warning projects
            critical_count: Number of critical projects
        
        Returns:
            Number of clients notified
        """
        message = WebSocketMessage(
            event_type=EventType.HEALTH_UPDATED,
            data={
                "overall_health": overall_health,
                "healthy_count": healthy_count,
                "warning_count": warning_count,
                "critical_count": critical_count,
            },
        )
        return await self._connection_manager.broadcast(message)
    
    async def broadcast_error_detected(
        self,
        project_id: str,
        error_type: str,
        error_message: str,
        severity: str,
    ) -> int:
        """Broadcast an error detection event.
        
        Args:
            project_id: Project where error was detected
            error_type: Type of error
            error_message: Error description
            severity: Error severity (low, medium, high, critical)
        
        Returns:
            Number of clients notified
        """
        message = WebSocketMessage(
            event_type=EventType.ERROR_DETECTED,
            data={
                "project_id": project_id,
                "error_type": error_type,
                "error_message": error_message,
                "severity": severity,
            },
        )
        return await self._connection_manager.broadcast(message)
    
    async def broadcast_to_topic(
        self,
        topic: str,
        event_type: EventType,
        data: dict[str, Any],
    ) -> int:
        """Broadcast a message to subscribers of a specific topic.
        
        Args:
            topic: Topic to broadcast to
            event_type: Type of event
            data: Event data
        
        Returns:
            Number of clients notified
        """
        if topic not in self._subscribers:
            return 0
        
        message = WebSocketMessage(event_type=event_type, data=data)
        sent_count = 0
        
        for conn_id in self._subscribers[topic]:
            if await self._connection_manager.send_to(conn_id, message):
                sent_count += 1
        
        return sent_count
    
    def get_stats(self) -> dict[str, Any]:
        """Get WebSocket manager statistics.
        
        Returns:
            Dictionary with connection and subscription stats
        """
        return {
            "active_connections": self._connection_manager.get_connection_count(),
            "topics": {
                topic: len(subscribers)
                for topic, subscribers in self._subscribers.items()
            },
            "connections": self._connection_manager.get_connection_info(),
        }
