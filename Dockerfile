FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/VOTRE-USERNAME/VOTRE-REPO
LABEL org.opencontainers.image.description="AGI-EVE Container"

WORKDIR /app

# Optimisation des layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Sécurité : utilisateur non-root
RUN adduser --disabled-password --gecos '' agi-user
USER agi-user

EXPOSE 8000

CMD ["python", "core/main.py"]
