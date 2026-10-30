FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DTH_DATA_DIR=/app/data DTH_CONFIG_DIR=/app/config

WORKDIR /app
COPY README.md /app/README.md
COPY backend /app/backend
RUN pip install --no-cache-dir "/app/backend[data,scheduler]"

EXPOSE 8000
CMD ["uvicorn", "dth.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
