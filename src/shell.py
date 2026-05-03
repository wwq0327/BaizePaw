import readline
import os
from .conversation import Conversation
from .event import DoneEvent, ErrorEvent, ToolEvent

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".shell_history")


class Shell:
    def __init__(self):
        self.conversation = Conversation()
        self.running = True
        self._setup_history()

    def _setup_history(self):
        try:
            readline.read_history_file(HISTORY_FILE)
        except FileNotFoundError:
            pass
        readline.set_history_length(200)

    def _save_history(self):
        try:
            readline.write_history_file(HISTORY_FILE)
        except Exception:
            pass

    def start(self):
        print("BaizePaw v0.3 - Your personal agent (type 'quit' to exit)")
        print("-" * 40)
        self.conversation.start()

        while self.running:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    self.running = False
                    continue

                readline.add_history(user_input)
                self._save_history()
                self.conversation.submit(user_input)

                # poll 循环，直到收到 DoneEvent 或 ErrorEvent
                while True:
                    events = self.conversation.poll()
                    for ev in events:
                        if isinstance(ev, ToolEvent):
                            print(f"  [tool] {ev.tool_name} → {ev.result}")
                        elif isinstance(ev, DoneEvent):
                            print(f"\nBaizePaw: {ev.content}")
                        elif isinstance(ev, ErrorEvent):
                            print(f"\nError: {ev.message}")
                    # DoneEvent 或 ErrorEvent 表示一轮结束
                    if events and any(isinstance(e, (DoneEvent, ErrorEvent)) for e in events):
                        break

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")

        self.conversation.stop()
