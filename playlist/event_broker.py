# playlist/event_broker.py
import threading
import time
import json

class EventBroker:
    """
    Simple in-process pub/sub for Server-Sent Events (SSE).
    Suitable for development / single-process runserver. For multi-process production
    use Redis pub/sub or Django Channels.
    """
    def __init__(self):
        self.cond = threading.Condition()
        self.events = []  # list of (ts, event_dict)

    def publish(self, event):
        """Publish a JSON-serializable event dict to all listeners."""
        with self.cond:
            self.events.append((time.time(), event))
            # keep buffer bounded
            if len(self.events) > 2000:
                self.events = self.events[-2000:]
            self.cond.notify_all()

    def listen(self, last_index=0):
        """
        Generator yielding (index, json_payload) for events with index >= last_index.
        Index is position within the current buffer (0-based).
        """
        idx = last_index
        while True:
            with self.cond:
                while idx >= len(self.events):
                    # wake periodically for heartbeats
                    self.cond.wait(timeout=15)
                while idx < len(self.events):
                    _, ev = self.events[idx]
                    yield idx, json.dumps(ev)
                    idx += 1
            time.sleep(0.001)  # small sleep to avoid busy spin

# singleton broker
broker = EventBroker()
