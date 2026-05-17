### Stage 1: Build frontend
FROM node:18-alpine AS frontend-build
WORKDIR /src-frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

### Stage 2: Runtime image
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source
COPY backend /app

# Copy built frontend into the backend static directory
RUN mkdir -p /app/frontend_dist
COPY --from=frontend-build /src-frontend/dist /app/frontend_dist

ENV PORT=8080
EXPOSE 8080

# Run uvicorn on the configured PORT (Cloud Run sets $PORT env)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
