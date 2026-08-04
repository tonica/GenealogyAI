# GenealogyAI - Frontend (React)

Frontend SPA de la aplicacion en React 18 + TypeScript + Vite + Tailwind CSS.

Consume el contrato de API `/api/v1` del backend (DTOs estables). Incluye:

- **Dashboard**: resumen del árbol (personas, familias, eventos, lugares, fuentes, media, calidad media, tareas, última importación).
- **Búsqueda**: filtros por texto libre, nombre, cognom, sexo, lugar y año de nacimiento (React Hook Form + Zod).
- **Persona**: detalle con relaciones (padres, cónyuges, hijos), línea de tiempo, factores de calidad, posibles duplicados y tareas de investigación.
- **Familias**: listado y detalle de familias.
- **Estadísticas**: agregados visualizados con Recharts.
- **Calidad**: informe general y por persona, duplicados y tareas de investigación.

## Stack

| Capa      | Tecnología                                                    |
| --------- | ------------------------------------------------------------- |
| UI        | React 18, React Router 6, Tailwind CSS, Heroicons             |
| Datos     | TanStack Query, React Hook Form + Zod                         |
| Gráficos  | Recharts                                                      |
| Build     | Vite 6, TypeScript 5                                          |
| Tests     | Vitest + Testing Library                                      |

## Desarrollo

```bash
npm install
npm run dev          # http://localhost:5173 (proxy /api -> http://localhost:8000)
npm test             # vitest run
npm run lint         # eslint
npm run build        # tsc -b && vite build
```

Si el backend no corre en `localhost:8000`, apunta el proxy con
`VITE_API_TARGET` (ver `vite.config.ts`).

## Despliegue

`docker-compose.yml` (raiz del repo) construye el frontend con un Dockerfile
multi-stage (build con Node + serve con nginx) y proxya `/api/` al servicio
`backend`.
