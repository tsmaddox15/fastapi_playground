import time
from .celery_app import celery_app

@celery_app.task
def long_task(duration: int):
    """Simulate a long-running Selenium like task"""
    try:
        for i in range(duration):
            time.sleep(1)
        return f"Task completed in {duration} seconds!"
    except Exception as e:
        return f"Task failed with exception {e}"