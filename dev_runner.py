from watchfiles import run_process

from bot.services.google_services.sheets_client import RequestSheetManager


def main():
    run_process(
        "bot",
        target="python run.py",
        target_type="command",
    )
    # mgr = RequestSheetManager()


if __name__ == "__main__":
    main()