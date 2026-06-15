FROM python:3.13-slim-bookworm
LABEL authors="wyattbrashear"

WORKDIR /app

RUN pip install --no-cache-dir beautifulsoup4 flask requests scikit-learn gunicorn

COPY . .

EXPOSE 80

ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120"]
