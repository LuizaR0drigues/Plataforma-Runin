# Stage 1: instala as dependências
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

# requirements primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
	&& rm -rf /var/lib/apt/lists/*
# Stage 2: imagem final
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# usuário sem privilégios; /app/staticfiles criada aqui para que o volume
# do docker-compose herde a permissão do appuser (collectstatic precisa escrever nela)
RUN useradd -m -r appuser && \
    mkdir -p /app/staticfiles && \
    chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

# código do projeto
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "forms.wsgi:application"]
