FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cart /app/cart
CMD ["uvicorn", "cart.api.router:app", "--host", "0.0.0.0", "--port", "8001"]
