# GenealogyAI

Aplicacion local de genealogia. Importa **GEDCOM 5.5.1**, persiste en
**SQLite**, expone una **API REST** con **FastAPI** y esta pensada para mostrar
los datos en un **frontend React**. Disenada como base para incorporar IA y
motores de busqueda genealogica en fases posteriores.

> **Estado actual**: backend funcional con parser GEDCOM propio, importador con
> normalizacion de fechas/lugares/apellidos, deteccion de errores y
> estadisticas, API REST endurecida (repositorios, pipeline de import, FTS5,
> UUID, audit log, PRAGMAs SQLite), **arquitectura hexagonal** (capa de dominio
> independiente de la persistencia con entities, value objects y services),
> **Data Quality Engine** (informe de calidad, deteccion de duplicados por
> reglas, score de calidad por factores, estadisticas avanzadas, sugerencias de
> investigacion) y **237 tests** con cobertura del 94%. El frontend React se
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
│  quality · duplicates ·       │
│  statistics · research/tasks  │
└──────────────┬────────────────┘
               │ schemas (Pydantic)
               ▼
┌───────────────────────────────┐
│     app/application           │  Use cases (UnitOfWork, DomainLoader)
│  GetPerson · ImportGedcom ·   │  Qualitat · Duplicats · Estadístiques
│  MergePersons · ...           │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│      app/domain (hexagonal)   │  Lógica de negocio PURA (sin I/O)
│  entities · value_objects ·   │  DateEngine · DuplicateRules ·
│  services · interfaces        │  QualityEngine · StatisticsEngine ·
│                               │  PlaceResolver · NameResolver ·
│                               │  DataQualityReport · ResearchTasks
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│     app/repositories          │  Capa de datos: Person/Family/PlaceRepo
│   BaseRepository (genérico)   │  implementa las interfaces de dominio
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│            SQLAlchemy          │  app/models (ORM) + app/db
│  person_fts · PRAGMAs · UUID   │
└───────────────────────────────┘
```

**Dirección de dependencias**: `API → Application → Domain ← Repositories ←
Infrastructure`. El dominio no conoce SQLAlchemy ni FastAPI; la persistencia
implementa las interfaces (`PersonRepositoryInterface`, ...) y la capa de
aplicación orquesta repositorios + motores de dominio (ver `DomainLoader`).

### Flujo de una importación

```
GEDCOM → validator (errores, coherencia)
        → normalizer (fechas, lugares, apellidos, slug/soundex)
        → resolver (dedupe de lugares/personas, refs cruzadas)
        → importer (persiste a SQLite)
        → pipeline (commit + opcional "rebuild" del índice FTS5)
```

### Data Quality Engine (Sprint 1.6)

Capa de **inteligencia genealógica** construida sobre el dominio. Solo analiza
datos (lectura), nunca los modifica.

| Motor | Responsabilidad |
| ----- | --------------- |
| `DateEngine` + `DateValue` | Parsea fechas GEDCOM (`1880`, `JAN 1880`, `ABT`, `BEF`, `AFT`, `BET X AND Y`, `FROM X TO Y`, `EST`, `CAL`, `INT`, ISO) y soporta intervalos, comparación, contención y solapamiento. |
| `DuplicateDetector` + rules | Reglas configurables (`NameRule`, `BirthRule`, `DeathRule`, `ParentsRule`, `MarriageRule`, `ChildrenRule`, `PlaceRule`) que puntúan posibles duplicados (umbral 0.55 por defecto). |
| `QualityEngine` | Score 0..1 por persona desglosado en factores explicables (nombre, sexo, nacimiento, defunción, padres, hijos, fuentes, eventos, lugares, cronología). |
| `StatisticsEngine` | Agregados: sexo, edades medias, nacimientos/defunciones por año, top lugares/cognomes, ramas más grandes, personas sin datos. |
| `PlaceResolver` / `NameResolver` | Detectan variantes de topónimos (`Cataluña`/`Cataluna`) y de nombres (`Maria`/`María`, `Jose`/`José`/`Josep`). |
| `DataQualityReportGenerator` | Informe completo de observaciones (errores, warnings, infos) exportable a JSON y Markdown. |
| `ResearchTaskGenerator` | Sugiere investigaciones (bautismo, matrimonio, defunción, padres, revisar duplicado) según las carencias. |

La capa de aplicación (`app/application/domain_loader.py`) carga las entidades
de dominio desde los repositorios (enriqueciendo fechas vitales desde los
eventos y las relaciones familiares) y los use cases de `quality.py` orquestan
los motores para los endpoints.

**Endpoints nuevos** (todos de solo lectura):

| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| GET | `/api/quality/report?format=json\|markdown` | Informe completo de calidad de datos. |
| GET | `/api/quality/person/{id}` | Score de calidad individual con factores. |
| GET | `/api/duplicates?limit=N` | Candidatos a personas duplicadas ordenados por puntuación. |
| GET | `/api/statistics` | Estadísticas agregadas del conjunto. |
| GET | `/api/research/tasks?limit=N` | Tareas de investigación sugeridas. |

---

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
pytest --cov=app            # cobertura (objetivo >= 90 %)
ruff check app tests
black --check app tests
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
- **Fase 3.6 (hecha — capa de dominio / hexagonal)**: entities, value objects,
  services e interfaces de dominio; mappers ORM<->dominio; UnitOfWork y use
  cases de aplicación (GetPerson, ImportGedcom, MergePersons); repositorios
  implementando las interfaces de dominio.
- **Fase 3.7 (hecha — Data Quality & Genealogical Intelligence)**: DateEngine,
  DuplicateDetector por reglas, QualityEngine, StatisticsEngine avanzado,
  resolvers de lugares/nombres, DataQualityReport, ResearchTaskGenerator y
  5 endpoints de calidad (237 tests, cobertura 94 %).
- **Fase 4:** frontend React (Vite) consumidor de la API.
- **Fase 5:** IA y motores de busqueda genealogica (usa FTS5 + fonetica).

## Licencia
Proyecto privado de fines formativos. Sin licencia publica asignada.