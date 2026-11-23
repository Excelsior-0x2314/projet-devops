# Projet DevOps : pipeline CI/CD pour une API conteneurisée sur AWS

![CI](https://github.com/Excelsior-0x2314/projet-devops/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/Excelsior-0x2314/projet-devops/actions/workflows/cd.yml/badge.svg)

Une petite API de gestion de tâches (FastAPI) livrée par un pipeline complet : du `git push` au déploiement automatique sur un serveur AWS EC2, avec lint, tests, scan de sécurité et possibilité de rollback.

## Architecture

```mermaid
graph LR
    Dev["Développeur"] -->|"git push"| GH["GitHub"]
    GH --> CI["CI : lint, tests, build Docker, scan Trivy"]
    CI -->|"succès sur main"| CD["CD : build et push de l'image"]
    CD --> GHCR["GHCR : registre d'images"]
    CD -->|"SSH puis docker pull"| EC2["EC2 AWS : conteneur Docker"]
    User["Utilisateur"] -->|"HTTP"| EC2
`````

## Stack

| Élément | Choix |
|---|---|
| API | FastAPI (Python) |
| Conteneur | Docker multi-stage, utilisateur non-root |
| Orchestration locale | Docker Compose (avec healthcheck) |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |
| Serveur | AWS EC2 (Ubuntu), région Stockholm |
| Qualité | ruff (lint), pytest (tests) |
| Sécurité | Trivy (scan de vulnérabilités), secrets GitHub, groupe de sécurité restreint |

## Routes de l'API

| Route | Rôle |
|---|---|
| `GET /` | Message de bienvenue |
| `GET /health` | État de l'API (utilisé par le healthcheck et le déploiement) |
| `GET /tasks` | Liste les tâches |
| `POST /tasks` | Crée une tâche (`{"title": "..."}`) |
| `DELETE /tasks/{id}` | Supprime une tâche |

Les tâches sont gardées en mémoire (pas de base de données).

## Lancer le projet en local

Avec Docker :

```bash
git clone https://github.com/Excelsior-0x2314/projet-devops.git
cd projet-devops
docker compose up --build -d
curl http://127.0.0.1:8000/health
docker compose down
```

Ou directement l'image publiée par le pipeline :

```bash
docker run --rm -p 8000:8000 ghcr.io/excelsior-0x2314/projet-devops:latest
```

Sans Docker :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

La documentation interactive est disponible sur `http://127.0.0.1:8000/docs`.

## Qualité du code

```bash
ruff check .
python -m pytest -v
```

## Le pipeline

### CI (`.github/workflows/ci.yml`)

Déclenchée à chaque push sur `main` et à chaque pull request.

1. **test** : lint (ruff) puis tests (pytest).
2. **docker-build** : build de l'image, puis scan Trivy. Le job échoue si une faille CRITICAL ou HIGH avec correctif disponible est trouvée.

### CD (`.github/workflows/cd.yml`)

Déclenchée automatiquement quand la CI réussit sur `main`.

1. **publish** : build de l'image et push sur GHCR avec deux tags : `latest` et le SHA du commit.
2. **deploy** : connexion SSH au serveur, téléchargement de l'image du SHA exact, redémarrage du conteneur, puis vérification de `/health` depuis GitHub.

Chaque image est identifiable par le SHA du commit qui l'a produite, ce qui rend le retour en arrière possible.

### Rollback (`.github/workflows/rollback.yml`)

Lancé à la main depuis l'onglet Actions (**Run workflow**) avec le SHA complet (40 caractères) de la version à redéployer. Les SHA disponibles sont listés dans le package GHCR du dépôt.

## Configuration du déploiement

Le job `deploy` et le rollback restent inactifs tant que la variable `DEPLOY_ENABLED` ne vaut pas `true`, ce qui évite d'échouer quand aucun serveur n'existe.

| Type | Nom | Rôle |
|---|---|---|
| Secret | `SSH_PRIVATE_KEY` | Clé privée de déploiement |
| Secret | `SSH_USER` | Utilisateur SSH (`ubuntu`) |
| Secret | `SSH_HOST` | Adresse IP publique du serveur |
| Variable | `DEPLOY_ENABLED` | `true` pour activer le déploiement |

## Sécurité

- Aucun secret dans le code : tout passe par les secrets GitHub.
- Conteneur exécuté avec un utilisateur non-root.
- Image scannée par Trivy à chaque build, paquets système mis à jour dans le Dockerfile.
- Groupe de sécurité AWS minimal : SSH (restreint) et HTTP uniquement.
- Clé SSH dédiée au déploiement, distincte de la clé personnelle.

## Coûts

Le serveur EC2 n'est lancé que pour les tests de déploiement, puis résilié. Un budget d'alerte AWS est configuré.

## Structure du dépôt

```text
projet-devops/
├── app/                      # code de l'API
├── tests/                    # tests unitaires
├── Dockerfile                # image multi-stage
├── docker-compose.yml        # lancement local avec healthcheck
├── requirements.txt          # dépendances de l'API
├── requirements-dev.txt      # dépendances de dev (ruff)
└── .github/workflows/
    ├── ci.yml                # lint, tests, build, scan
    ├── cd.yml                # publication de l'image et déploiement
    └── rollback.yml          # retour à une version précédente
```

## Pistes d'amélioration

- Infrastructure as Code avec Terraform (EC2 et groupe de sécurité).
- Monitoring avec Prometheus et Grafana.
- HTTPS avec un nom de domaine.
- Déploiement sans ouvrir le port SSH à tous (par exemple via AWS Systems Manager).
- Base de données PostgreSQL.
