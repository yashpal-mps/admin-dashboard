FROM python:3.11-slim

WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"] 