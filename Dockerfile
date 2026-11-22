# --- Étape 1 : installation des dépendances ---
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Étape 2 : image finale ---
FROM python:3.12-slim

# Correctifs de sécurité des paquets système (ex. zlib1g)
RUN apt-get update \
    && apt-get install -y --only-upgrade zlib1g \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser

WORKDIR /home/appuser
COPY --from=builder /install /usr/local
COPY app ./app

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
