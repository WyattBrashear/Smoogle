FROM python:3.13.12-slim-bookworm
LABEL authors="wyattbrashear"
WORKDIR /app
COPY . /app

RUN "python3 -m pip install beautifulsoup4>=4.14.3 flask>=3.1.3 requests>=2.32.5 scikit-learn>=1.8.0, gunicorn"

ENTRYPOINT ["gunicorn", "app:app", "--bind", "5000"]