"""Importador específic per al GEDCOM real de MyHeritage.

Cas de prova: el fitxer exportat per MyHeritage
`8d3d1m_673630le1515in5bb7db68_A.ged` — 330 persones i 100 famílies.

Ús:
    php -m scripts.import_real_gedcom --ged PATH [--out DIR]

Comportament:
  - Llegeix el fitxer GEDCOM (no l'escriu mai: només lectura).
  - El parseja i comprova la coherència (references, dates, duplicats, noms).
  - Persisteix a un SQLite temporal i independent al fitxer original.
  - Verifica els comptes (330 persones / 100 famílies).
  - Genera un informe final en Markdown.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.logging import get_logger, log_import_summary, setup_logging
from app.importer import GedcomParseError, parse
from app.services.importer import import_gedcom

EXPECTED = {"persons": 330, "families": 100}

logger = get_logger("scripts.import_real_gedcom")


def build_report(result, issues) -> str:
    stats = result.stats
    surnames = sorted(stats.surname_frequency.items(), key=lambda kv: -kv[1])

    lines: list[str] = [
        "# Informe d'importació — GEDCOM MyHeritage",
        "",
        f"_Generat el {datetime.now():%Y-%m-%d %H:%M}._",
        "",
        "## Resum general",
        "",
        "| Mètrica | Valor |",
        "|---|---|",
        f"| Persones | {result.persons} |",
        f"| Famílies | {result.families} |",
        f"| Fonts (SOUR) | {result.sources} |",
        f"| Mitjans (OBJE) | {result.media} |",
        f"| Llocs singulars | {result.places} |",
        f"| Esdeveniments | {result.events} |",
        f"| Fills relacionats | {result.children} |",
        "",
        "## Verificació de comptes",
        "",
    ]
    rows = [
        ("Persones", result.persons, EXPECTED["persons"]),
        ("Famílies", result.families, EXPECTED["families"]),
    ]
    ok = True
    for label, got, want in rows:
        status = "OK" if got == want else "FAIL"
        ok = ok and got == want
        lines.append(f"- **{label}**: {got} (esperat {want}) → **{status}**")
    lines.extend(["", f"**Resultat global:** {'SUPERAT' if ok else 'FALLIT'}", ""])

    lines.append("## Coherència de dades")
    lines.append("")
    if not issues:
        lines.append("_Cap problema detectat._")
    else:
        lines.append("| Nivell | Codi | Xref | Missatge |")
        lines.append("|---|---|---|---|")
        for iss in issues:
            lines.append(f"| {iss.level} | {iss.code} | {iss.xref} | {iss.message} |")
    lines.append("")

    lines.append("## Esdeveniments per tipus")
    lines.append("")
    lines.append("| Tipus | Quantitat |")
    lines.append("|---|---|")
    for key in sorted(stats.events_by_type):
        lines.append(f"| {key} | {stats.events_by_type[key]} |")
    lines.append("")

    lines.append("## Cognoms més freqüents (top 15)")
    lines.append("")
    lines.append("| Cognom | Persones |")
    lines.append("|---|---|")
    for name, count in surnames[:15]:
        lines.append(f"| {name} | {count} |")
    lines.append("")

    lines.append("## Estadístiques completes (JSON)")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2, default=str))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    setup_logging()
    p = argparse.ArgumentParser(description="Importa el GEDCOM real de MyHeritage.")
    p.add_argument("ged", type=str, help="Path del fitxer .ged")
    p.add_argument(
        "--out",
        default="_data",
        help="Carpeta on escriure l'informe .md i la DB SQLite (postf-destí).",
    )
    args = p.parse_args()

    source = Path(args.ged)
    if not source.exists():
        logger.error("no existeix el fitxer: %s", source)
        return 2

    logger.info("[1/4] Parsejant (sols lectura): %s", source)
    try:
        doc = parse(source)
    except GedcomParseError as exc:
        logger.error("error de parse: %s", exc)
        return 1

    from app.services.stats import detect_errors

    issues = detect_errors(doc)
    logger.info(
        "parse ok: %s persones, %s famílies, %s fonts, %s mitjans, %s problemes",
        len(doc.persons),
        len(doc.families),
        len(doc.sources),
        len(doc.media),
        len(issues),
    )

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / "genealogyai_real.db"
    db_path.unlink(missing_ok=True)

    logger.info("[2/4] Persistint a SQLite independent: %s", db_path)
    engine = create_engine(
        f"sqlite+pysqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    import app.models  # noqa: F401 —— garanteix models registrats
    from app.db.session import Base

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        result = import_gedcom(session, doc)
        session.commit()
    log_import_summary(
        logger,
        {
            "persons": result.persons,
            "families": result.families,
            "sources": result.sources,
            "media": result.media,
            "places": result.places,
            "events": result.events,
            "issues": len(issues),
            "time_ms": getattr(result, "elapsed_ms", 0) or 0,
        },
    )

    logger.info("[3/4] Verificació de comptes")
    rows = [
        ("Persones", result.persons, EXPECTED["persons"]),
        ("Famílies", result.families, EXPECTED["families"]),
    ]
    ok = True
    for label, got, want in rows:
        mark = "OK" if got == want else "FAIL"
        ok = ok and got == want
        logger.info("  %s: %s (esperat %s) [%s]", label, got, want, mark)
    logger.info("  Resultat vital: %s", "SUCCESS" if ok else "FAIL")

    logger.info("[4/4] Problemes de coherència: %s", len(issues))
    for iss in issues:
        logger.info("  [%s] %s %s: %s", iss.level, iss.code, iss.xref, iss.message)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"informe_import_{stamp}.md"
    out_file.write_text(build_report(result, issues), encoding="utf-8")
    logger.info("\nInforme final: %s", out_file)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
