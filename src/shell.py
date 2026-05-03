import readline
import os
from .conversation import Conversation
from .event import DoneEvent, ErrorEvent, ToolEvent

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".shell_history")


class Shell:
    def __init__(self):
        self.chat_conversation = Conversation()
        self.coach_conversation = None
        self.active_conversation = self.chat_conversation
        self.mode = "chat"
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

    def _handle_command(self, text: str) -> bool:
        if text == "/coach":
            self.mode = "coach"
            if self.coach_conversation is None:
                from .coach import Coach

                knowledge_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "knowledge",
                )
                coach = Coach(knowledge_dir)
                self.coach_conversation = Conversation(core=coach.core)
                self.coach_conversation.start()
            self.active_conversation = self.coach_conversation
            print("[Switched to Coach mode]")
            return True
        elif text == "/chat":
            self.mode = "chat"
            self.active_conversation = self.chat_conversation
            print("[Switched to Chat mode]")
            return True
        return False

    def start(self):
        print("BaizePaw v0.5 - Your personal agent (type 'quit' to exit)")
        print("-" * 40)
        self.chat_conversation.start()

        while self.running:
            prompt = "You [coach]: " if self.mode == "coach" else "You: "
            try:
                user_input = input(f"\n{prompt}").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    self.running = False
                    continue

                readline.add_history(user_input)
                self._save_history()

                if self._handle_command(user_input):
                    continue

                self.active_conversation.submit(user_input)

                # poll 循环，直到收到 DoneEvent 或 ErrorEvent
                while True:
                    events = self.active_conversation.poll()
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

        self.chat_conversation.stop()
        if self.coach_conversation is not None:
            self.coach_conversation.stop()
