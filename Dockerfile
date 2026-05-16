FROM python:3.12-slim

WORKDIR /

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="opt/venv/bin:$PATH"

COPY src/. ./app

ENV PYTHONPATH=.

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

USER root