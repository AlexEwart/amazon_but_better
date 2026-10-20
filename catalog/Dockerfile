FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY catalog /app/catalog
COPY request_logging.py /app/request_logging.py
CMD ["uvicorn", "catalog.api.router:app", "--host", "0.0.0.0", "--port", "8002"]
