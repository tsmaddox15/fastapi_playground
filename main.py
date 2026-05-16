import os
import concurrent
from fastapi import FastAPI, BackgroundTasks
from celery.result import AsyncResult
from tasks import long_task
from celery_app import celery_app
from sqlalchemy import create_engine, text, inspect
from celery.result import AsyncResult
import time
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
import psutil
import threading
app = FastAPI()
engine = create_engine("sqlite:///results.sqlite", echo=False)

def print_thread_info():
    current_process = psutil.Process(os.getpid())
    parent_process = psutil.Process(os.getppid())
    
    # OS threads in this specific process
    os_threads = current_process.num_threads()
    # Python-managed threads in this specific process
    py_threads = threading.active_count()
    print(f"--- Startup Thread Report ---")
    print(f"REPORT FROM PID: {os.getpid()} (Parent PID: {os.getppid()})")
    print(f"Threads in THIS process (OS level): {os_threads}")
    print(f"Threads in THIS process (Python level): {py_threads}")
    print(f"Active Thread Names: {[t.name for t in threading.enumerate()]}")
    
    print("-" * 30)

@app.on_event("startup")
async def startup():
    loop = asyncio.get_event_loop()
    executor = loop.run_in_executor(None, lambda: None) 
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=30) # pool of threads.#https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor
    #asyncio.get_event_loop().set_default_executor(executor) # setting this gets rid of async thread https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.get_event_loop
    #print(f"Executor max workers: {executor._max_workers}")  
    
    print(f"Max async workers: {loop._default_executor._max_workers}")
    process = psutil.Process(os.getpid())
    
    thread_count = process.num_threads()
    active_threads = threading.active_count()
    
    print(f"--- Startup Thread Report ---")
    print(f"Process ID: {os.getpid()}")
    print(f"Total OS threads (psutil): {thread_count}")
    print(f"Python active threads: {active_threads}")
    print(f"\n--- Active Threads Report (PID: {os.getpid()}) ---")
    threads = threading.enumerate()
    for idx, thread in enumerate(threads):
        print(f"{idx+1}. Name: {thread.name} | ID: {thread.ident} | Daemon: {thread.daemon}")

    print(f"-----------------------------")
 
@app.get("/thread")
def thread_info():
    print_thread_info()
    return ""
@app.get("/run-task/{duration}")
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

"""Endpoints used to show event loop thread being blocked.""" 

@app.get("/blocking")
async def blocking():
    print(f"Start blocking: {datetime.now()}")
    pid = os.getpid()
    print(f"Process {pid}")
    #time sleep is sync and blocks the thread
    time.sleep(15)

    print(f"End blocking: {datetime.now()}")
    return {"message": "blocking endpoint done"}


@app.get("/blocking")
async def blocking():
    print(f"Start blocking: {datetime.now()}")
    pid = os.getpid()
    print(f"Process {pid}")
    #time sleep is sync and blocks the thread
    time.sleep(15)

    print(f"End blocking: {datetime.now()}")
    return {"message": "blocking endpoint done"}


@app.get("/non_blocking")
async def non_blocking():
    """"""
    print(f"Start non-blocking: {datetime.now()}")
    pid = os.getpid()
    print(f"Process {pid}")
    # Async version which will use the event loop.
    await asyncio.sleep(2)

    print(f"End non-blocking: {datetime.now()}")
    return {"message": "non-blocking endpoint done"}

# =====================================================================
@app.get("/sync")
def sync():
    print(f"Start sync: {datetime.now()}")
    pid = os.getpid()
    print(f"Process {pid}")
    #time sleep is sync and blocks the thread
    time.sleep(7)

    print(f"End sync: {datetime.now()}")
    return {"message": "sync response"}

@app.get("/blocking_task")
async def index(background_tasks: BackgroundTasks):
    """Shows that running our blocking task in background will block the entire event loop if something tries to run after."""
    background_tasks.add_task(blocking)

    return {"message": "response returned immediately"}


def do_work():
    try:
        raise Exception("doesn't resolve at the endpoint") # this doesn't go to except in the endpoint
    except Exception as e:
        pass
    raise Exception("Endpoint handles") # this gets captured in the endpoint to mimic unhandled exceptions.

@app.get("/try_example")
async def try_example():
    """Example of how wrapping your endpoint can always do some type of exception behavior"""
    try:
        do_work()
    except Exception as e:
        return {"error": str(e)}
    else:
        return "Finished request"