import asyncio
from typing import Dict, List
from app.protocols.message_schema import AgentMessage

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        self.history: Dict[str, List[AgentMessage]] = {}

    def subscribe(self, incident_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if incident_id not in self.subscribers:
            self.subscribers[incident_id] = []
        self.subscribers[incident_id].append(queue)
        return queue

    def unsubscribe(self, incident_id: str, queue: asyncio.Queue):
        if incident_id in self.subscribers:
            if queue in self.subscribers[incident_id]:
                self.subscribers[incident_id].remove(queue)

    async def publish(self, incident_id: str, message: AgentMessage):
        if incident_id not in self.history:
            self.history[incident_id] = []
        self.history[incident_id].append(message)

        if incident_id in self.subscribers:
            for q in list(self.subscribers[incident_id]):
                await q.put(message)

    def get_messages(self, incident_id: str) -> List[AgentMessage]:
        return self.history.get(incident_id, [])

event_bus = EventBus()