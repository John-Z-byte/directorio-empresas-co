from __future__ import annotations

from pathlib import Path
import pandas as pd

from directorio.config import DATA_DIR
from directorio.logging_utils import setup_logger, StepTimer

logger = setup_logger()

def aggregate_tipo_sociedad(run_date: str) -> None:
    t = StepTimer.start("gold_agg_tipo_sociedad")

    gold_base = DATA_DIR / "gold" / f"run_date={run_date}" / "empresas.parquet"
    out_dir = DATA_DIR / "gold" / "analytics"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = out_dir / f"empresas_por_tipo_sociedad_{run_date}.csv"

    logger.info(f"agg | start | run_date={run_date}")
    logger.info(f"agg | input={gold_base.as_posix()}")

    df = pd.read_parquet(
        gold_base,
        columns=["tipo_sociedad", "estado_matricula", "fecha_matricula"]
    )

    # derivar año
    df["anio_matricula"] = df["fecha_matricula"].dt.year

    # group
    agg = (
        df.groupby(
            ["tipo_sociedad", "estado_matricula", "anio_matricula"],
            dropna=False
        )
        .size()
        .reset_index(name="empresas_count")
        .sort_values(
            ["anio_matricula", "tipo_sociedad", "estado_matricula"]
        )
    )

    agg.to_csv(out_csv, index=False, encoding="utf-8")

    logger.info(f"agg | output={out_csv.as_posix()} rows={len(agg):,}")
    logger.info(f"agg | done | seconds={t.done():.2f}")

if __name__ == "__main__":
    aggregate_tipo_sociedad("2026-01-03")
