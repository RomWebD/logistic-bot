# celery_worker_entry.py
import os

if os.getenv("DEBUG") == "1":
    import debugpy
    debugpy.listen(("0.0.0.0", 5679))
    print("🪲 Debugger listening on port 5679 (Celery Worker)")

from bot.celery_app import celery_app

if __name__ == "__main__":
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--pool=solo",   # важливо для дебагу, prefork не працює з debugpy
    ])
