import sys
from src.shell import Shell


def main():
    if "--cli" in sys.argv:
        shell = Shell()
        shell.start()
    else:
        from src.tui.app import BaizePawApp
        app = BaizePawApp()
        app.run()


if __name__ == "__main__":
    main()
