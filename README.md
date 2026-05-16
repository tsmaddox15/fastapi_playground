# Celery and Concurrency Testing.
This is a simple fastapi for testing different concurrency models and using celery.


## Run locally.
Following need to be running. 

1. `uv run uvicorn src.main:app`
2. `celery -A src.celery_app.celery_app worker --loglevel=info --concurrency 2`
    * If running on windows you will need to change the pool to threads since the default is pools, which windows doesn't support. `celery -A src.celery_app.celery_app worker --loglevel=info --pool threads --concurrency 2`

## Running in docker
You can simply run the docker with build to have everything run. `docker compose up --build`

---

## Sources
Most of the talking points below come from either the book [Fluent Python](https://www.amazon.com/Fluent-Python-Concise-Effective-Programming/dp/1491946008) or from reading [official python docs](https://docs.python.org/3/). This app has code that I used to help my understanding of the concepts from these two sources. There are also great examples in the book you can review for free in this [git repo](https://github.com/fluentpython/example-code-2e/tree/master/19-concurrency).

## Understanding the Python Process


---
## Python Concurrency
3 main models.
* Threading
* Multiprocessing
* Async

### Threading

### Multiprocessing

### Asyncio

---
## Sync vs Async Hosting

### Uvicorn

### Gunicorn

---

## Celery Worker Examples
![alt text](image.png)



![1 concurrent worker](image-2.png)
![1 worker 4 task](image-4.png)
![alt text](image-7.png)

![8 concurrent worker](image-1.png)
![8 workers 8 repeated task](image-3.png)
![alt text](image-6.png)