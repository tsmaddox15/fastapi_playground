from fastapi import FastAPI
from celery.result import AsyncResult
from tasks import long_task
from celery_app import celery_app
from sqlalchemy import create_engine, text, inspect
from celery.result import AsyncResult
app = FastAPI()
engine = create_engine("sqlite:///results.sqlite", echo=False)

@app.post("/run-task/{duration}")
def run_task(duration: int):
    """Start a background task and return its ID"""
    task = long_task.delay(duration)
    return {"task_id": task.id}

@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    """Check the task’s current status"""
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }

@app.get("/jobs")
def list_jobs(limit: int = 20):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM celery_taskmeta ORDER BY date_done DESC LIMIT :limit"),
            {"limit": limit}
        ).fetchall()
        
    jobs = []
    for row in rows:
        async_result = AsyncResult(row.task_id, app=celery_app)
        jobs.append({
            "id": async_result.id,
            "status": async_result.status,
            "result": async_result.result
        })
    if jobs:
        return jobs
    else:
        return "No jobs"