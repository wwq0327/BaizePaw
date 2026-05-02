from .agent import AgentRunner

class Shell:
    def __init__(self):
        self.agent = AgentRunner()
        self.running = True

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