// Objecte central de mocks de l'API per als tests. Els fitxers de test el
// carreguen amb `await import()` dins de la factory de `vi.mock` (càrrega
// diferida a temps d'execució), de manera que no hi ha problemes d'hoisting.

export const apiMock = {
  dashboard: vi.fn(),
  searchPersons: vi.fn(),
  person: vi.fn(),
  personQuality: vi.fn(),
  families: vi.fn(),
  family: vi.fn(),
  statistics: vi.fn(),
  qualityReport: vi.fn(),
  duplicates: vi.fn(),
  researchTasks: vi.fn(),
}
