import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class _OrderWSManager:
    """Broadcasts order events to connected admin clients."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)
        logger.info("Admin WS connected  (total: %d)", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)
        logger.info("Admin WS disconnected (total: %d)", len(self._connections))

    async def broadcast(self, payload: dict) -> None:
        if not self._connections:
            return
        dead: set[WebSocket] = set()
        for ws in self._connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        self._connections -= dead


order_ws = _OrderWSManager()
