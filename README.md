# API Products – MSPR Bloc 4

Cette API fait partie du projet MSPR Bloc 4 et gère les opérations liées aux produits dans un système de microservices.

## Technologies utilisées

- **FastAPI** — Framework web rapide et moderne
- **MongoDB** — Base de données NoSQL (MongoDB Atlas)
- **RabbitMQ** — Message broker pour communication inter-services
- **Docker** — Conteneurisation
- **GitHub Actions** — CI/CD
- **SonarQube** — Analyse de code
- **Prometheus & Grafana** — Monitoring
- **JWT** — Authentification sécurisée

## Structure du projet

```
api-products/
│
├── app/
│   ├── db/                  # Connexion MongoDB
│   ├── messaging/           # Gestion RabbitMQ
│   ├── models/              # Modèles Pydantic
│   ├── routes/              # Endpoints FastAPI
│   ├── security/            # Authentification JWT
│   ├── services/            # Logique métier
│   └── utils/               # Fonctions utilitaires
│
├── tests/                   # Tests unitaires Pytest
├── .github/workflows/       # CI GitHub Actions
├── docker-compose.yml       # Services MongoDB, RabbitMQ
├── Dockerfile               # Conteneurisation de l'API
├── sonar-project.properties # Configuration SonarQube
└── README.md
```

## Lancer les tests

```bash
pytest --cov=app
```

## Lancer le projet localement

```bash
docker-compose up --build
```

L’API sera disponible sur `http://localhost:8000`.

## Authentification

L’API utilise JWT. Pour interagir avec les routes protégées, ajoutez un header :

```
Authorization: Bearer <votre_token>
```

## CI/CD

Un pipeline GitHub Actions exécute :

- Linting (pylint)
- Tests unitaires (pytest)
- Couverture de code
- Scan SonarQube
