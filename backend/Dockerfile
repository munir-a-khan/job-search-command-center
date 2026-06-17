FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TECTONIC_CACHE_DIR=/tmp/tectonic-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates fontconfig wget xz-utils \
      fonts-liberation fonts-dejavu-core \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz \
      -o /tmp/tectonic.tar.gz \
    && tar -xzf /tmp/tectonic.tar.gz -C /usr/local/bin tectonic \
    && rm /tmp/tectonic.tar.gz \
    && tectonic --version

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /data/resumes /data/cover_letters /tmp/tectonic-cache

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
