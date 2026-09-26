FROM python:3.12.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --system --uid 10001 --no-create-home appuser
COPY summary.py .
USER appuser
ENTRYPOINT ["python", "/app/summary.py"]
