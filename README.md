# Projet DevOps : pipeline CI/CD pour une API conteneurisée

![CI](https://github.com/Excelsior-0x2314/projet-devops/actions/workflows/ci.yml/badge.svg)

API de gestion de tâches (FastAPI) avec un pipeline CI/CD : lint, tests, build Docker, scan de sécurité, puis déploiement sur AWS.

## Lancer en local

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/health
```

## Pipeline CI (GitHub Actions)

1. Lint (ruff)
2. Tests (pytest)
3. Build de l'image Docker
4. Scan de vulnérabilités (Trivy)

*Documentation complète à venir.*
