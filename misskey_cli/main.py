from .migrate import run_upgrade
from .cli import MisskeyCLI


def main():
    run_upgrade()
    try:
        MisskeyCLI().cmdloop()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
