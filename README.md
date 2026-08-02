# GenealogyAI

Aplicacion local de genealogia. Importa **GEDCOM 5.5.1**, persiste en
**SQLite**, expone una **API REST** con **FastAPI** y esta pensada para mostrar
los datos en un **frontend React**. Disenada como base para incorporar IA y
motores de busqueda genealogica en fases posteriores.

> **Estado actual**: backend funcional con parser GEDCOM propio, importador con
> normalizacion de fechas/lugares/apellidos, deteccion de errores y
> estadisticas, API REST y 51 tests. El frontend React se implementara en una
> fase posterior.

---

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
ruff check app tests
black app tests
```

---

## Decisiones arquitectonicas

1. **Separacion en capas dentro de `app/`**
   - `api/`: routers FastAPI (capa de presentacion HTTP).
   - `core/`: configuracion y utilidades transversales.
   - `db/`: engine, sesiones, Base declarativa y punto central de modelos.
   - `models/`: modelos ORM (SQLAlchemy 2.0, estilo `Mapped`/`mapped_column`).
   - `schemas/`: schemas Pydantic v2 (validacion y serializacion).
   - `services/`: logica de negocio desacoplada del HTTP.
   - `importer/`: parser de GEDCOM, separado para poder testearlo en aislamiento.
   - `utils/`: helpers reutilizables.
   - `main.py`: punto de entrada del conentainer FastAPI.

2. **Configuracion tipada con `pydantic-settings`** (`core/config.py`)
   Una sola clase `Settings` con valores por defecto sanos y `lru_cache` para
   instanciarla una unica vez. Sobreescribible por variables de entorno (clave
   para Docker) y por un `.env` local.

3. **Conexion SQLite reutilizada**
   En `db/session.py` el motor se crea una vez en el arranque del modulo.
   `check_same_thread=False` permite que el engine sea compartido entre los
   hilos de FastAPI sin bloqueos (requisito de SQLite). `SessionLocal` es un
   `sessionmaker` que se configura con `autoflush=False` y
   `expire_on_commit=False` para que los objetos sigan siendo legibles tras el
   commit.

4. **Dependencia de sesion por request** (`get_db`)
   Se provee un `generator` que abre/commitea/cierra una sesion por request;
   el cierre se garantiza con `finally`. Este es el patron canonico FastAPI
   para depender de la base de datos.

5. **Base declarativa unica** (`Base`)
   Todos los modelos heredaran de una unica `DeclarativeBase` para que
   SQLAlchemy y Alembic las numeren de forma coherente.

6. **Endpoints minimos**
   `GET /api/health` y `GET /` verifican config, CORS, routing y contenedor;
   la API amplia CRUD con `/api/persons`, `/api/families`, `/api/places`,
   `/api/tree/{id}` y `POST /api/import`.

7. **Docker + Compose**
   - Imagen base `python:3.12-slim`.
   - Las dependencias se instalan antes de copiar el codigo (cache de capas).
   - Compose monta `./data:/data` y fija `DATABASE_URL` con pysqlite a esa
     ruta, de modo que la DB persiste entre reinicios.

8. **Alembic preparado**
   `alembic/env.py` importa `get_settings()` y los modelos; sobreescribe
   `sqlalchemy.url` con el valor de config para que las migraciones usen
   exactamente la misma conexion que la app.

9. **Testing listo para la fase 2**
   `tests/conftest.py` hace `samename` para resolver `app.*` y dos fixtures:
   `client` (TestClient) y `test_session` (SQLite en memoria) para los tests
   de logica de negocio que vendran.

---

## Hoja de ruta (fases futuras)

- **Fase 0 (hecha)**: scaffolding backend, Docker, Alembic, config tipada.
- **Fase 1 (hecha)**: modelos ORM (`Person`, `Family`, `Event`, `Place`,
  `Source`, `Media`, `Suggestion`) + migraciones Alembic.
- **Fase 2 (hecha)**: schemas Pydantic + CRUD por recursos.
- **Fase 3 (hecha)**: importador GEDCOM 5.5.1 -> SQLite con normalizacion,
  validacion de coherencia (referencias, fechas, duplicados) y estadisticas.
- **Fase 4:** frontend React (Vite) consumidor de la API.
- **Fase 5:** IA y motores de busqueda genealogica.

## Licencia
Proyecto privado de fines formativos. Sin licencia publica asignada.