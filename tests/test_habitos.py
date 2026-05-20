import csv
import subprocess
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from HabitosCarGross import (
    ACTIVITY_LEVELS,
    CarpenterGrossbergNetwork,
    assign_habit_level,
    binarize_rows,
    build_cluster_profiles,
    read_csv_dataset,
)
from PrepararDatasets import download_fitbit_with_kagglehub, prepare_fitbit_tracker, resolve_fitbit_dir


def test_network_groups_binary_activity_patterns_incrementally():
    network = CarpenterGrossbergNetwork(vigilance=0.8)

    labels = network.fit_predict(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
        ]
    )

    assert labels == [1, 2, 3, 3]
    assert len(network.prototypes) == 3


@pytest.mark.parametrize(
    ("metrics", "expected"),
    [
        ({"dias_activos_semana": 0.5, "minutos_activos_dia": 10, "sesiones_entrenamiento_semana": 0, "intensidad_promedio": 1.2, "competencias_anuales": 0}, "Sedentario"),
        ({"dias_activos_semana": 2, "minutos_activos_dia": 28, "sesiones_entrenamiento_semana": 1, "intensidad_promedio": 2.2, "competencias_anuales": 0}, "Levemente activo / Moderado"),
        ({"dias_activos_semana": 4, "minutos_activos_dia": 55, "sesiones_entrenamiento_semana": 4, "intensidad_promedio": 3.2, "competencias_anuales": 0}, "Activo"),
        ({"dias_activos_semana": 5, "minutos_activos_dia": 85, "sesiones_entrenamiento_semana": 6, "intensidad_promedio": 4.1, "competencias_anuales": 4}, "Atleta amateur / Competitivo"),
        ({"dias_activos_semana": 6.5, "minutos_activos_dia": 125, "sesiones_entrenamiento_semana": 10, "intensidad_promedio": 4.8, "competencias_anuales": 12}, "Atleta profesional / Elite"),
    ],
)
def test_assign_habit_level_maps_activity_score_to_five_requested_labels(metrics, expected):
    assert assign_habit_level(metrics) == expected
    assert expected in ACTIVITY_LEVELS


def test_binarize_rows_uses_activity_feature_medians():
    rows = [
        {"dias_activos_semana": "1", "minutos_activos_dia": "20"},
        {"dias_activos_semana": "3", "minutos_activos_dia": "40"},
        {"dias_activos_semana": "5", "minutos_activos_dia": "80"},
    ]

    binary_rows, thresholds = binarize_rows(rows, ["dias_activos_semana", "minutos_activos_dia"])

    assert thresholds == {"dias_activos_semana": 3.0, "minutos_activos_dia": 40.0}
    assert binary_rows == [[0, 0], [1, 1], [1, 1]]


def test_build_cluster_profiles_adds_habit_level_interpretation():
    rows = [
        {"dias_activos_semana": "0", "minutos_activos_dia": "8", "sesiones_entrenamiento_semana": "0", "intensidad_promedio": "1.1", "competencias_anuales": "0"},
        {"dias_activos_semana": "1", "minutos_activos_dia": "18", "sesiones_entrenamiento_semana": "0", "intensidad_promedio": "1.7", "competencias_anuales": "0"},
        {"dias_activos_semana": "6", "minutos_activos_dia": "130", "sesiones_entrenamiento_semana": "10", "intensidad_promedio": "4.7", "competencias_anuales": "12"},
    ]
    labels = [1, 1, 2]
    features = [
        "dias_activos_semana",
        "minutos_activos_dia",
        "sesiones_entrenamiento_semana",
        "intensidad_promedio",
        "competencias_anuales",
    ]
    thresholds = {
        "dias_activos_semana": 3,
        "minutos_activos_dia": 60,
        "sesiones_entrenamiento_semana": 4,
        "intensidad_promedio": 3,
        "competencias_anuales": 2,
    }

    profiles = build_cluster_profiles(rows, labels, features, thresholds)

    assert profiles[1]["habit_level"] == "Sedentario"
    assert profiles[2]["habit_level"] == "Atleta profesional / Elite"
    assert "bajo_minutos_activos_dia" in profiles[1]["label"]


def test_read_csv_dataset_ignores_identifier_and_reference_labels(tmp_path):
    path = tmp_path / "habitos.csv"
    fieldnames = [
        "id_persona",
        "nivel_referencia",
        "dias_activos_semana",
        "minutos_activos_dia",
        "sesiones_entrenamiento_semana",
        "intensidad_promedio",
        "competencias_anuales",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, 51):
            writer.writerow(
                {
                    "id_persona": i,
                    "nivel_referencia": "Activo",
                    "dias_activos_semana": i % 7,
                    "minutos_activos_dia": i * 2,
                    "sesiones_entrenamiento_semana": i % 10,
                    "intensidad_promedio": 1 + (i % 5),
                    "competencias_anuales": i % 12,
                }
            )

    _, features = read_csv_dataset(path, None, min_rows=50)

    assert features == [
        "dias_activos_semana",
        "minutos_activos_dia",
        "sesiones_entrenamiento_semana",
        "intensidad_promedio",
        "competencias_anuales",
    ]


def test_cli_generates_activity_results_and_summary(tmp_path):
    dataset = tmp_path / "habitos.csv"
    output = tmp_path / "resultados.csv"
    summary = tmp_path / "resumen.txt"
    features = [
        "dias_activos_semana",
        "minutos_activos_dia",
        "sesiones_entrenamiento_semana",
        "intensidad_promedio",
        "competencias_anuales",
    ]

    with dataset.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id_persona", *features])
        writer.writeheader()
        for i in range(1, 51):
            writer.writerow(
                {
                    "id_persona": i,
                    "dias_activos_semana": i % 7,
                    "minutos_activos_dia": 10 + i * 2,
                    "sesiones_entrenamiento_semana": i % 9,
                    "intensidad_promedio": 1 + (i % 5) * 0.8,
                    "competencias_anuales": i % 14,
                }
            )

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "HabitosCarGross.py"),
            "--input",
            str(dataset),
            "--id-column",
            "id_persona",
            "--rho",
            "0.8",
            "--output",
            str(output),
            "--summary",
            str(summary),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output.exists()
    assert summary.exists()
    assert "nivel_habito_estimado" in output.read_text(encoding="utf-8").splitlines()[0]
    assert "Categorias de habito solicitadas" in summary.read_text(encoding="utf-8")


def test_prepare_fitbit_tracker_aggregates_daily_activity_by_user(tmp_path):
    source_dir = tmp_path / "fitbit"
    source_dir.mkdir()
    source = source_dir / "dailyActivity_merged.csv"
    output = tmp_path / "fitbit_tracker_procesado.csv"
    fieldnames = [
        "Id",
        "ActivityDate",
        "TotalSteps",
        "TotalDistance",
        "TrackerDistance",
        "LoggedActivitiesDistance",
        "VeryActiveDistance",
        "ModeratelyActiveDistance",
        "LightActiveDistance",
        "SedentaryActiveDistance",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes",
        "Calories",
    ]
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({"Id": "101", "ActivityDate": "4/12/2016", "TotalSteps": "1000", "TotalDistance": "0.8", "TrackerDistance": "0.8", "LoggedActivitiesDistance": "0", "VeryActiveDistance": "0", "ModeratelyActiveDistance": "0", "LightActiveDistance": "0.8", "SedentaryActiveDistance": "0", "VeryActiveMinutes": "0", "FairlyActiveMinutes": "0", "LightlyActiveMinutes": "20", "SedentaryMinutes": "900", "Calories": "1800"})
        writer.writerow({"Id": "101", "ActivityDate": "4/13/2016", "TotalSteps": "12000", "TotalDistance": "8", "TrackerDistance": "8", "LoggedActivitiesDistance": "0", "VeryActiveDistance": "2", "ModeratelyActiveDistance": "1", "LightActiveDistance": "5", "SedentaryActiveDistance": "0", "VeryActiveMinutes": "40", "FairlyActiveMinutes": "20", "LightlyActiveMinutes": "180", "SedentaryMinutes": "700", "Calories": "2300"})
        writer.writerow({"Id": "202", "ActivityDate": "4/12/2016", "TotalSteps": "300", "TotalDistance": "0.2", "TrackerDistance": "0.2", "LoggedActivitiesDistance": "0", "VeryActiveDistance": "0", "ModeratelyActiveDistance": "0", "LightActiveDistance": "0.2", "SedentaryActiveDistance": "0", "VeryActiveMinutes": "0", "FairlyActiveMinutes": "0", "LightlyActiveMinutes": "5", "SedentaryMinutes": "1200", "Calories": "1500"})

    prepare_fitbit_tracker(source_dir, output)

    rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
    assert len(rows) == 2
    assert rows[0]["id_persona"] == "FB-101"
    assert rows[0]["fuente"] == "FitBit Fitness Tracker Data"
    assert rows[0]["nivel_referencia"] == "sin_etiqueta_supervisada"
    assert float(rows[0]["minutos_activos_dia"]) == 130.0
    assert float(rows[0]["sesiones_entrenamiento_semana"]) > 0
    assert int(rows[0]["competencias_anuales"]) == 0


def test_download_fitbit_with_kagglehub_uses_kaggle_dataset_slug(monkeypatch, tmp_path):
    calls = []
    fake_kagglehub = types.SimpleNamespace(
        dataset_download=lambda slug: calls.append(slug) or str(tmp_path)
    )
    monkeypatch.setitem(sys.modules, "kagglehub", fake_kagglehub)

    path = download_fitbit_with_kagglehub()

    assert path == tmp_path
    assert calls == ["arashnic/fitbit"]


def test_resolve_fitbit_dir_downloads_with_kagglehub(monkeypatch, tmp_path):
    monkeypatch.setattr("PrepararDatasets.download_fitbit_with_kagglehub", lambda: tmp_path)

    assert resolve_fitbit_dir() == tmp_path
