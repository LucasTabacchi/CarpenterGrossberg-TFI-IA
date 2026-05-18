import csv
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CarGross import (
    CarpenterGrossbergNetwork,
    build_cluster_profiles,
    binarize_rows,
    read_csv_dataset,
)


def test_network_creates_new_cluster_when_vigilance_rejects_match():
    network = CarpenterGrossbergNetwork(vigilance=0.8)

    labels = network.fit_predict(
        [
            [1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1],
        ]
    )

    assert labels == [1, 1, 2]
    assert network.prototypes == [[1, 1, 0, 0, 0], [0, 0, 0, 1, 1]]


def test_network_retries_second_best_cluster_before_creating_one():
    network = CarpenterGrossbergNetwork(vigilance=0.75)
    network.fit_predict(
        [
            [1, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
        ]
    )

    label = network.predict_one([0, 0, 1, 1])

    assert label == 2
    assert len(network.prototypes) == 2


def test_binarize_rows_uses_feature_medians_when_thresholds_are_not_given():
    rows = [
        {"frecuencia": "1", "monto": "100"},
        {"frecuencia": "3", "monto": "300"},
        {"frecuencia": "5", "monto": "500"},
    ]

    binary_rows, thresholds = binarize_rows(rows, ["frecuencia", "monto"])

    assert thresholds == {"frecuencia": 3.0, "monto": 300.0}
    assert binary_rows == [[0, 0], [1, 1], [1, 1]]


def test_binarize_rows_uses_given_thresholds_instead_of_medians():
    rows = [
        {"frecuencia": "1", "monto": "100"},
        {"frecuencia": "3", "monto": "300"},
        {"frecuencia": "5", "monto": "500"},
    ]

    binary_rows, thresholds = binarize_rows(rows, ["frecuencia", "monto"], {"frecuencia": 4, "monto": 250})

    assert thresholds == {"frecuencia": 4, "monto": 250}
    assert binary_rows == [[0, 0], [0, 1], [1, 1]]


def test_binarize_rows_rejects_empty_or_non_numeric_values():
    rows = [{"frecuencia": "", "monto": "100"}]

    with pytest.raises(ValueError, match="Valor no numerico"):
        binarize_rows(rows, ["frecuencia", "monto"])


def test_read_csv_dataset_rejects_missing_feature(tmp_path):
    path = tmp_path / "clientes.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id_cliente", "monto"])
        writer.writeheader()
        writer.writerow({"id_cliente": "1", "monto": "10"})

    with pytest.raises(ValueError, match="no existe en el CSV"):
        read_csv_dataset(path, ["frecuencia"], min_rows=1)


def test_infer_numeric_features_skips_identifier_columns(tmp_path):
    path = tmp_path / "clientes.csv"
    fieldnames = ["id_cliente", "frecuencia", "monto", "recencia", "descuento", "variedad"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, 51):
            writer.writerow(
                {
                    "id_cliente": i,
                    "frecuencia": i,
                    "monto": i * 10,
                    "recencia": 60 - i,
                    "descuento": i % 2,
                    "variedad": i % 5,
                }
            )

    _, selected_features = read_csv_dataset(path, None, min_rows=50)

    assert selected_features == ["frecuencia", "monto", "recencia", "descuento", "variedad"]


def test_network_rejects_invalid_rho():
    with pytest.raises(ValueError, match="vigilancia"):
        CarpenterGrossbergNetwork(vigilance=1.2)


def test_build_cluster_profiles_uses_original_feature_averages():
    rows = [
        {"frecuencia": "8", "monto": "200", "recencia": "10", "descuento": "1", "variedad": "5"},
        {"frecuencia": "6", "monto": "180", "recencia": "12", "descuento": "1", "variedad": "4"},
        {"frecuencia": "1", "monto": "40", "recencia": "50", "descuento": "0", "variedad": "1"},
    ]
    labels = [1, 1, 2]
    features = ["frecuencia", "monto", "recencia", "descuento", "variedad"]
    thresholds = {"frecuencia": 4, "monto": 100, "recencia": 30, "descuento": 0.5, "variedad": 3}

    profiles = build_cluster_profiles(rows, labels, features, thresholds)

    assert "alto_monto" in profiles[1]["label"]
    assert "bajo_recencia" in profiles[1]["label"]
    assert profiles[1]["averages"]["frecuencia"] == 7.0
    assert "bajo_monto" in profiles[2]["label"]


def test_cli_rejects_missing_id_column_before_writing_output(tmp_path):
    dataset = tmp_path / "clientes.csv"
    output = tmp_path / "resultados.csv"
    summary = tmp_path / "resumen.txt"

    with dataset.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["frecuencia", "monto", "recencia", "descuento", "variedad"],
        )
        writer.writeheader()
        for i in range(1, 51):
            writer.writerow(
                {
                    "frecuencia": i % 10 + 1,
                    "monto": i * 20,
                    "recencia": 60 - i,
                    "descuento": i % 3,
                    "variedad": i % 7 + 1,
                }
            )

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "CarGross.py"),
            "--input",
            str(dataset),
            "--features",
            "frecuencia,monto,recencia,descuento,variedad",
            "--id-column",
            "id_cliente",
            "--output",
            str(output),
            "--summary",
            str(summary),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "columna identificadora" in result.stderr
    assert not output.exists()


def test_cli_generates_result_and_summary_files(tmp_path):
    dataset = tmp_path / "clientes.csv"
    output = tmp_path / "resultados.csv"
    summary = tmp_path / "resumen.txt"

    with dataset.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id_cliente", "frecuencia", "monto", "recencia", "descuento", "variedad"],
        )
        writer.writeheader()
        for i in range(1, 51):
            writer.writerow(
                {
                    "id_cliente": i,
                    "frecuencia": i % 10 + 1,
                    "monto": i * 20,
                    "recencia": 60 - i,
                    "descuento": i % 3,
                    "variedad": i % 7 + 1,
                }
            )

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "CarGross.py"),
            "--input",
            str(dataset),
            "--features",
            "frecuencia,monto,recencia,descuento,variedad",
            "--id-column",
            "id_cliente",
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
    summary_text = summary.read_text(encoding="utf-8")
    output_text = output.read_text(encoding="utf-8")
    assert "Cantidad de clientes procesados: 50" in summary_text
    assert "Analisis de sensibilidad por rho" in summary_text
    assert "Promedios por cluster e interpretacion" in summary_text
    assert "cluster" in output_text.splitlines()[0]
    assert "cluster_1" not in output_text


def test_cli_can_run_with_inferred_features_without_using_id_column(tmp_path):
    dataset = tmp_path / "clientes.csv"
    output = tmp_path / "resultados.csv"
    summary = tmp_path / "resumen.txt"

    with dataset.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id_cliente", "frecuencia", "monto", "recencia", "descuento", "variedad"],
        )
        writer.writeheader()
        for i in range(1, 51):
            writer.writerow(
                {
                    "id_cliente": i,
                    "frecuencia": i % 10 + 1,
                    "monto": i * 20,
                    "recencia": 60 - i,
                    "descuento": i % 3,
                    "variedad": i % 7 + 1,
                }
            )

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "CarGross.py"),
            "--input",
            str(dataset),
            "--id-column",
            "id_cliente",
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
    assert "Variables: frecuencia, monto, recencia, descuento, variedad" in summary.read_text(encoding="utf-8")
