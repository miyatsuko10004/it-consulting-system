FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly (mock setup)
RUN pip install fastapi uvicorn sqlalchemy jinja2 python-multipart faker

COPY . /app

# Run seed data script and then start the server
CMD python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
