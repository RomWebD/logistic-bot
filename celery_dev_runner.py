from watchfiles import run_process

def main():
    run_process(
        "bot",  # відслідковуємо зміни у bot/
        target="python celery_worker_entry.py",
        target_type="command",
    )

if __name__ == "__main__":
    main()
