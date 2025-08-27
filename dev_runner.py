from watchfiles import run_process


def main():
    run_process(
        "bot",
        target="python run.py",
        target_type="command",
    )


if __name__ == "__main__":
    main()