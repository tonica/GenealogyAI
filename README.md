# GenealogyAI

Aplicacion local de genealogia. Importa **GEDCOM 5.5.1**, persiste en
**SQLite**, expone una **API REST** con **FastAPI** y esta pensada para mostrar
los datos en un **frontend React**. Disenada como base para incorporar IA y
motores de busqueda genealogica en fases posteriores.

> **Estado actual**: backend funcional con parser GEDCOM propio, importador con
> normalizacion de fechas/lugares/apellidos, deteccion de errores y
> estadisticas, API REST endurecida (repositorios, pipeline de import, FTS5,
> UUID, audit log, PRAGMAs SQLite) y **64 tests**. El frontend React se
> implementara en una fase posterior.

---

## Arquitectura

```
Client HTTP (test/curl)
        │
        ▼
┌───────────────────────────────┐
│            app/api            │  Routers FastAPI (endpoints REST)
│  persons · families · places  │
│  trees · import · health      │
└──────────────┬────────────────┘
               │ schemas (Pydantic)
               ▼
┌───────────────────────────────┐
│        app/repositories        │  Capa de datos: Person/Family/PlaceRepo
│   BaseRepository (genérico)   │  (API → repository → SQLAlchemy)
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│            SQLAlchemy          │  app/models (ORM) + app/db
│  person_fts · PRAGMAs · UUID   │
└───────────────────────────────┘
                                     Servicios auxiliares:
┌────────────────────────────┐       ┌─────────────────────────────┐
│ app/services/import_pipeline │       │  app/services/search.py     │
│ Validator→Normalizer→        │       │  soundex · metaphone ·       │
│ Resolver→Importer (etapas)   │       │  SearchIndexer (FTS5)        │
└────────────────────────────┘       └─────────────────────────────┘
```

### Flujo de una importación

```
GEDCOM → validator (errores, coherencia)
        → normalizer (fechas, lugares, apellidos, slug/soundex)
        → resolver (dedupe de lugares/personas, refs cruzadas)
        → importer (persiste a SQLite)
        → pipeline (commit + opcional "rebuild" del índice FTS5)
```

---

## Stack

## Stack

| Capa     | Tecnologia                                   |
| -------- | -------------------------------------------- |
| Backend  | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Datos    | SQLite (via SQLAlchemy)                       |
| Schemas  | Pydantic v2 + pydantic-settings               |
| Server   | uvicorn                                       |
| Frontend | React (pendiente)                              |
| Infra    | Docker, docker-compose                         |
| Calidad  | pytest, ruff, black                            |

---

## Requisitos

- Docker + Docker Compose (opcional para desarrollo local: Python 3.12).

## Uso rapido con Docker

```bash
# Construye y arranca el backend
docker compose up --build

# La API queda disponible en:
http://localhost:8000            # raiz
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/api/health # comprobacion de salud
```

Para lanzarlo en background:

```bash
docker compose up -d --build
docker compose logs -f backend
```

La base de datos SQLite y los archivos GEDCOM viven en `./data/`, montada como
volumen en el contenedor.

## Desarrollo local (sin Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Migraciones (Alembic)

```bash
cd backend
alembic revision --autogenerate -m "crear modelos"
alembic upgrade head
```

### Tests, formato y estilo

```bash
cd backend
pytest
ruff check app tests
black app tests
```

---

## Decisiones arquitectonicas

1. **Separacion en capas dentro de `app/`**
   - `api/`: routers FastAPI (capa de presentacion HTTP).
   - `core/`: configuracion y utilidades transversales (config, logging).
   - `db/`: engine, sesiones, Base declarativa y punto central de modelos.
   - `models/`: modelos ORM (SQLAlchemy 2.0, estilo `Mapped`/`mapped_column`).
   - `repositories/`: capa de acceso a datos (repositorios genéricos y por recurso).
   - `schemas/`: schemas Pydantic v2 (validacion y serializacion).
   - `services/`: logica de negocio desacoplada del HTTP (import pipeline, search).
   - `importer/`: parser de GEDCOM, separado para poder testearlo en aislamiento.
   - `utils/`: helpers reutilizables.
   - `main.py`: punto de entrada del contenedor FastAPI.

2. **Configuracion tipada con `pydantic-settings`** (`core/config.py`)
   Una unica clase `Settings` con sub-settings `database`, `logging`, `import_`,
   `search` y `ai`. Delimitador de anidamiento `__` para variables de entorno
   (p. ej. `DATABASE__URL`), con fallback a la `DATABASE_URL` plana para Docker.

3. **Repository pattern** (`repositories/`)
   El API depende de repositorios (`BaseRepository` generico + `PersonRepository`,
   `FamilyRepository`, `PlaceRepository`), no de la sesion directamente.
   Facilita el testeo y centraliza las consultas y eager-loads.

4. **Conexion SQLite endurecida** (`db/session.py`)
   Se aplican PRAGMAs por conexion (via `event.listens_for`) para un SQLite
   robusto: `journal_mode=WAL`, `foreign_keys=ON`, `synchronous=NORMAL`,
   `cache_size`, `temp_store=MEMORY` y `busy_timeout`.
   `check_same_thread=False` permite compartir el engine entre hilos de FastAPI.
   `SessionLocal` usa `autoflush=False` y `expire_on_commit=False`.

5. **Dependencia de sesion por request** (`get_db`)
   Generator que abre/commitea/cierra una sesion por request; el cierre se
   garantiza con `finally`. Patron canonico FastAPI.

6. **UUID en las entidades** (`models/mixins.py`)
   Mixin `UUIDMixin` aporta `uuid` (String(36)) único a Person, Family, Place,
   Event, Source, Media, Suggestion y AuditLog, ademas del id autoincremental.

7. **Audit log** (`models/audit_log.py`)
   Entidad `AuditLog` para registrar acciones sobre entidades (tipo, id, accion,
   usuario, payload JSON) con base para trazabilidad futura.

8. **Busqueda full-text (FTS5)** (`services/search.py`)
   `SearchIndexer` crea una tabla virtual `person_fts` (external content sobre
   `persons`) y expone `search()` y `rebuild()`. Los algoritmos `soundex` y
   `metaphone` preparan la futura busqueda fonetica.

9. **Pipeline de import en etapas** (`services/import_pipeline/`)
   `Validator` -> `Normalizer` -> `Resolver` -> `Importer`, orquestados por
   `ImportPipeline`; devuelve un `ImportResult` con estadisticas y tiempo.

10. **Registro estructurado** (`core/logging.py`)
    `setup_logging()` configura handlers y formato (JSON opcional);
    `get_logger(name)` devuelve loggers `genealogyai.*`. No se usa `print()`.

11. **Endpoints minimos**
    `GET /api/health` y `GET /` verifican config, CORS, routing y contenedor;
    la API amplia CRUD con `/api/persons`, `/api/families`, `/api/places`,
    `/api/tree/{id}` y `POST /api/import`.

12. **Docker + Compose**
    - Imagen base `python:3.12-slim`.
    - Las dependencias se instalan antes de copiar el codigo (cache de capas).
    - Compose monta `./data:/data` y fija `DATABASE_URL` a esa ruta.

13. **Alembic preparado**
    `alembic/env.py` importa `get_settings()` y los modelos; sobreescribe
    `sqlalchemy.url` con el valor de config para que las migraciones usen
    exactamente la misma conexion que la app.

14. **Testing listo para la fase 2**
    `tests/conftest.py` hace `samename` para resolver `app.*` y fixtures
    `client`, `test_session` y `sqlite_session` (SQLite en memoria) para los
    tests de logica, API, FTS, UUID y PRAGMAs.

---

## Hoja de ruta (fases futuras)

- **Fase 0 (hecha)**: scaffolding backend, Docker, Alembic, config tipada.
- **Fase 1 (hecha)**: modelos ORM (`Person`, `Family`, `Event`, `Place`,
  `Source`, `Media`, `Suggestion`) + migraciones Alembic.
- **Fase 2 (hecha)**: schemas Pydantic + CRUD por recursos.
- **Fase 3 (hecha)**: importador GEDCOM 5.5.1 -> SQLite con normalizacion,
  validacion de coherencia (referencias, fechas, duplicados) y estadisticas.
- **Fase 3.5 (hecha — hardening)**: arquitectura endurecida con repository
  pattern, pipeline de import en etapas, FTS5 + Soundex/Metaphone, UUID en las
  entidades, AuditLog, PRAGMAs SQLite, config tipada central, logging
  estructurado y cobertura de tests (64).
- **Fase 4:** frontend React (Vite) consumidor de la API.
- **Fase 5:** IA y motores de busqueda genealogica (usa FTS5 + fonetica).

## Licencia
Proyecto privado de fines formativos. Sin licencia publica asignada.