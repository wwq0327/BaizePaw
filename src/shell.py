import readline
import os
from .agent import AgentRunner

# 持久化命令历史文件
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".shell_history")


class Shell:
    def __init__(self):
        self.agent = AgentRunner()
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
        print("BaizePaw v0.1 - Your personal agent (type 'quit' to exit)")
        print("-" * 40)

        while self.running:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    self.running = False
                    continue

                response = self.agent.run(user_input)
                print(f"\nBaizePaw: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self._save_history()
