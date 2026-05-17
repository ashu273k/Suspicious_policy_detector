# Single container: FastAPI backend + built Vite frontend

FROM node:18-alpine AS frontend-build
WORKDIR /src-frontend

COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app

RUN mkdir -p /app/frontend_dist
COPY --from=frontend-build /src-frontend/dist /app/frontend_dist

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
