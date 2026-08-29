FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["sh", "-c", "uvicorn src.frame_finder.api.main:app --host 0.0.0.0 --port $PORT"]