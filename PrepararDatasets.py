#!/usr/bin/env python
"""Prepara datasets para HabitosCarGross.py.

Dataset 1: UCI Human Activity Recognition Using Smartphones.
Dataset 2: FitBit Fitness Tracker Data.
"""

from __future__ import annotations

import argparse
import csv
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


UCI_HAR_URL = "https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip"
FITBIT_KAGGLE_SLUG = "arashnic/fitbit"
FEATURES = [
    "dias_activos_semana",
    "minutos_activos_dia",
    "sesiones_entrenamiento_semana",
    "intensidad_promedio",
    "competencias_anuales",
]


def prepare_uci_har(output_path: Path, work_dir: Path) -> None:
    """Descarga UCI HAR y crea un CSV agregado por persona/sujeto."""
    archive_path = work_dir / "uci_har.zip"
    extract_dir = work_dir / "uci_har"
    work_dir.mkdir(parents=True, exist_ok=True)

    if not archive_path.exists():
        urllib.request.urlretrieve(UCI_HAR_URL, archive_path)

    if not extract_dir.exists():
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)

    inner_archive = extract_dir / "UCI HAR Dataset.zip"
    root = extract_dir / "UCI HAR Dataset"
    if inner_archive.exists() and not root.exists():
        with zipfile.ZipFile(inner_archive) as archive:
            archive.extractall(extract_dir)

    if not root.exists():
        raise ValueError("No se encontro la carpeta 'UCI HAR Dataset' dentro del archivo UCI.")
    subject_counts: dict[int, Counter[int]] = defaultdict(Counter)

    for split in ("train", "test"):
        subject_file = root / split / f"subject_{split}.txt"
        label_file = root / split / f"y_{split}.txt"
        subjects = [int(line.strip()) for line in subject_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        labels = [int(line.strip()) for line in label_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        for subject, label in zip(subjects, labels):
            subject_counts[subject][label] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["id_persona", "fuente", "nivel_referencia", *FEATURES]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for subject in sorted(subject_counts):
            counts = subject_counts[subject]
            total = sum(counts.values())
            active = counts[1] + counts[2] + counts[3]
            walking = counts[1]
            stairs = counts[2] + counts[3]
            active_rate = active / total
            stairs_rate = stairs / total
            walking_rate = walking / total

            dias = round(1 + active_rate * 6, 2)
            minutos = round(15 + active_rate * 95 + stairs_rate * 15, 2)
            sesiones = round(1 + walking_rate * 5 + stairs_rate * 3, 2)
            intensidad = round(min(5.0, 1 + active_rate * 3.2 + stairs_rate * 1.2), 2)

            writer.writerow(
                {
                    "id_persona": f"UCI-{subject:03d}",
                    "fuente": "UCI HAR Smartphones",
                    "nivel_referencia": "sin_etiqueta_supervisada",
                    "dias_activos_semana": dias,
                    "minutos_activos_dia": minutos,
                    "sesiones_entrenamiento_semana": sesiones,
                    "intensidad_promedio": intensidad,
                    "competencias_anuales": 0,
                }
            )


def prepare_fitbit_tracker(input_dir: Path, output_path: Path) -> None:
    """Agrega archivos dailyActivity_merged.csv de FitBit por usuario."""
    if not input_dir.exists():
        raise ValueError(f"No existe la carpeta del dataset FitBit: {input_dir}")

    daily_files = sorted(input_dir.rglob("dailyActivity_merged.csv"))
    if not daily_files:
        raise ValueError(f"No se encontraron archivos dailyActivity_merged.csv en {input_dir}")

    stats: dict[str, dict[str, object]] = {}
    required = {
        "Id",
        "ActivityDate",
        "TotalSteps",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes",
    }

    for daily_file in daily_files:
        with daily_file.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                missing = sorted(required - set(reader.fieldnames or []))
                raise ValueError(f"El archivo FitBit no tiene las columnas requeridas: {', '.join(missing)}")

            for row in reader:
                user_id = row["Id"].strip()
                if not user_id:
                    continue
                current_date = parse_fitbit_date(row["ActivityDate"])
                steps = float(row["TotalSteps"])
                very_active = float(row["VeryActiveMinutes"])
                fairly_active = float(row["FairlyActiveMinutes"])
                lightly_active = float(row["LightlyActiveMinutes"])
                active_minutes = very_active + fairly_active + lightly_active

                user_stats = stats.setdefault(
                    user_id,
                    {
                        "first_date": current_date,
                        "last_date": current_date,
                        "rows": 0,
                        "active_days": 0,
                        "active_minutes_sum": 0.0,
                        "workout_sessions": 0,
                        "weighted_intensity_sum": 0.0,
                    },
                )
                user_stats["first_date"] = min(user_stats["first_date"], current_date)
                user_stats["last_date"] = max(user_stats["last_date"], current_date)
                user_stats["rows"] += 1
                user_stats["active_minutes_sum"] += active_minutes
                user_stats["weighted_intensity_sum"] += lightly_active * 1.5 + fairly_active * 3.0 + very_active * 5.0

                if active_minutes >= 20 or steps >= 3000:
                    user_stats["active_days"] += 1
                if very_active + fairly_active >= 10 or steps >= 7500:
                    user_stats["workout_sessions"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["id_persona", "fuente", "nivel_referencia", *FEATURES]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for user_id in sorted(stats, key=lambda value: int(value) if value.isdigit() else value):
            item = stats[user_id]
            observed_days = max(1, (item["last_date"] - item["first_date"]).days + 1)
            observed_weeks = max(observed_days / 7, 1)
            active_minutes = item["active_minutes_sum"]
            intensity = item["weighted_intensity_sum"] / active_minutes if active_minutes else 1.0

            writer.writerow(
                {
                    "id_persona": f"FB-{user_id}",
                    "fuente": "FitBit Fitness Tracker Data",
                    "nivel_referencia": "sin_etiqueta_supervisada",
                    "dias_activos_semana": round(min(7.0, item["active_days"] / observed_weeks), 2),
                    "minutos_activos_dia": round(active_minutes / item["rows"], 2),
                    "sesiones_entrenamiento_semana": round(item["workout_sessions"] / observed_weeks, 2),
                    "intensidad_promedio": round(intensity, 2),
                    "competencias_anuales": 0,
                }
            )


def download_fitbit_with_kagglehub() -> Path:
    """Descarga FitBit desde KaggleHub y devuelve la carpeta local del dataset."""
    try:
        import kagglehub
    except ImportError as exc:
        raise ValueError(
            "No se encontro kagglehub. Instale dependencias con: python -m pip install -r requirements.txt"
        ) from exc

    return Path(kagglehub.dataset_download(FITBIT_KAGGLE_SLUG))


def resolve_fitbit_dir() -> Path:
    return download_fitbit_with_kagglehub()


def parse_fitbit_date(raw_value: str) -> date:
    for pattern in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return date.strptime(raw_value.strip(), pattern)
        except ValueError:
            continue
    raise ValueError(f"Fecha FitBit invalida: {raw_value!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepara datasets para la red de habitos.")
    parser.add_argument("--datasets-dir", type=Path, default=Path("datasets"))
    parser.add_argument("--work-dir", type=Path, default=Path("datasets") / "_raw")
    parser.add_argument("--skip-uci", action="store_true", help="No descargar UCI HAR.")
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.skip_uci:
        prepare_uci_har(args.datasets_dir / "uci_har_habitos_procesado.csv", args.work_dir)

    fitbit_dir = resolve_fitbit_dir()
    prepare_fitbit_tracker(fitbit_dir, args.datasets_dir / "fitbit_tracker_procesado.csv")
    print(f"Datasets generados en {args.datasets_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
