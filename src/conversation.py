import queue
import threading
from typing import List

from .core import Core
from .event import ErrorEvent, Event


class Conversation:
    def __init__(self, core=None):
        self._core = core if core is not None else Core()
        self._in: queue.Queue = queue.Queue()
        self._out: List[Event] = []
        self._out_lock = threading.Lock()
        self._running = False
        self._worker: threading.Thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def stop(self):
        self._running = False
        self._in.put(None)  # sentinel to unblock worker

    def submit(self, text: str):
        self._in.put(text)

    def poll(self) -> List[Event]:
        with self._out_lock:
            events = list(self._out)
            self._out.clear()
        return events

    def _run(self):
        while self._running:
            try:
                text = self._in.get(timeout=0.5)
            except queue.Empty:
                continue
            if text is None:
                break
            try:
                for event in self._core.run_iter(text):
                    with self._out_lock:
                        self._out.append(event)
            except Exception as e:
                with self._out_lock:
                    self._out.append(ErrorEvent(message=str(e)))
