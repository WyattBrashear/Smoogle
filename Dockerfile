FROM python:3.13.12-slim-bookworm
LABEL authors="wyattbrashear"
WORKDIR /app
COPY . /app

RUN "pip install beautifulsoup4 flask requests scikit-learn gunicorn"

ENTRYPOINT ["gunicorn", "app:app", "--bind", "5000"]