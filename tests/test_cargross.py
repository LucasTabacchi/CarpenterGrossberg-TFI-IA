import csv
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CarGross import (
    CarpenterGrossbergNetwork,
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


def test_read_csv_dataset_rejects_missing_feature(tmp_path):
    path = tmp_path / "clientes.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id_cliente", "monto"])
        writer.writeheader()
        writer.writerow({"id_cliente": "1", "monto": "10"})

    with pytest.raises(ValueError, match="no existe en el CSV"):
        read_csv_dataset(path, ["frecuencia"], min_rows=1)


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
    assert "Cantidad de clientes procesados: 50" in summary.read_text(encoding="utf-8")
    assert "cluster" in output.read_text(encoding="utf-8").splitlines()[0]
