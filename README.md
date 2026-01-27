Simple fastapi app for playing with celery.

Following need to be running. 

1.) uv run uvicorn main:app
2.) celery -A celery_app.celery_app worker --loglevel=info
