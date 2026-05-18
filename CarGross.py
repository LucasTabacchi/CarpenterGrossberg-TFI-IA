#!/usr/bin/env python
"""CarGross.py: implementacion de la red Carpenter-Grossberg.

La version clasica trabaja con patrones binarios y aprendizaje no supervisado.
Este programa recibe un CSV, convierte variables numericas a 0/1 mediante
umbrales, aplica la red y guarda el cluster asignado a cada fila.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter
from pathlib import Path


class CarpenterGrossbergNetwork:
    """Red Carpenter-Grossberg clasica para clustering binario incremental."""

    def __init__(self, vigilance: float = 0.8) -> None:
        if not 0 <= vigilance <= 1:
            raise ValueError("El valor de vigilancia rho debe estar entre 0 y 1.")
        self.vigilance = vigilance
        self.prototypes: list[list[int]] = []
        self._width: int | None = None

    def fit_predict(self, patterns: list[list[int]]) -> list[int]:
        """Aprende una secuencia de patrones y devuelve clusters desde 1."""
        return [self.predict_one(pattern) for pattern in patterns]

    def predict_one(self, pattern: list[int]) -> int:
        """Clasifica un patron y adapta el prototipo ganador."""
        self._validate_pattern(pattern)

        if not self.prototypes:
            self.prototypes.append(pattern.copy())
            return 1

        active = set(range(len(self.prototypes)))
        while active:
            winner = max(active, key=lambda idx: (self._matching_score(self.prototypes[idx], pattern), -idx))
            similarity = self._vigilance_similarity(self.prototypes[winner], pattern)

            if similarity >= self.vigilance:
                self.prototypes[winner] = [
                    stored_bit & input_bit for stored_bit, input_bit in zip(self.prototypes[winner], pattern)
                ]
                return winner + 1

            active.remove(winner)

        self.prototypes.append(pattern.copy())
        return len(self.prototypes)

    def _validate_pattern(self, pattern: list[int]) -> None:
        if not pattern:
            raise ValueError("Cada patron debe tener al menos una variable.")
        if any(bit not in (0, 1) for bit in pattern):
            raise ValueError("La red Carpenter-Grossberg clasica solo acepta patrones binarios 0/1.")
        if self._width is None:
            self._width = len(pattern)
        elif len(pattern) != self._width:
            raise ValueError("Todos los patrones deben tener la misma cantidad de variables.")

    @staticmethod
    def _matching_score(prototype: list[int], pattern: list[int]) -> float:
        """Puntaje bottom-up normalizado usado para elegir candidato."""
        overlap = sum(stored_bit & input_bit for stored_bit, input_bit in zip(prototype, pattern))
        prototype_norm = sum(prototype)
        if prototype_norm == 0:
            return 1.0 if sum(pattern) == 0 else 0.0
        return overlap / (0.5 + prototype_norm)

    @staticmethod
    def _vigilance_similarity(prototype: list[int], pattern: list[int]) -> float:
        """Test de vigilancia: |T AND X| / |X|."""
        pattern_norm = sum(pattern)
        overlap = sum(stored_bit & input_bit for stored_bit, input_bit in zip(prototype, pattern))
        if pattern_norm == 0:
            return 1.0 if sum(prototype) == 0 else 0.0
        return overlap / pattern_norm


def parse_feature_list(raw_features: str | None) -> list[str] | None:
    if raw_features is None:
        return None
    features = [feature.strip() for feature in raw_features.split(",") if feature.strip()]
    if not features:
        raise ValueError("Debe indicar al menos una variable en --features.")
    return features


def read_csv_dataset(path: Path, features: list[str] | None, min_rows: int = 50) -> tuple[list[dict[str, str]], list[str]]:
    """Lee un CSV y valida cantidad minima de filas y variables."""
    if not path.exists():
        raise ValueError(f"No existe el archivo de entrada: {path}")

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("El CSV no tiene encabezados.")
        rows = list(reader)
        fieldnames = reader.fieldnames

    if len(rows) < min_rows:
        raise ValueError(f"El dataset debe tener al menos {min_rows} filas. Filas encontradas: {len(rows)}.")

    selected_features = features or infer_numeric_features(rows, fieldnames)
    missing = [feature for feature in selected_features if feature not in fieldnames]
    if missing:
        raise ValueError(f"La variable '{missing[0]}' no existe en el CSV.")

    if len(selected_features) < 5:
        raise ValueError("El TFI pide al menos 5 variables de entrada.")

    return rows, selected_features


def infer_numeric_features(rows: list[dict[str, str]], fieldnames: list[str]) -> list[str]:
    """Selecciona automaticamente columnas numericas."""
    numeric_features: list[str] = []
    for field in fieldnames:
        if is_identifier_column(field):
            continue
        try:
            for row in rows:
                parse_number(row[field])
        except ValueError:
            continue
        numeric_features.append(field)
    if len(numeric_features) < 5:
        raise ValueError("No se pudieron inferir 5 variables numericas. Use --features.")
    return numeric_features[:5]


def is_identifier_column(field: str) -> bool:
    """Detecta columnas identificadoras que no deben usarse como variables."""
    normalized = field.strip().lower().replace("-", "_").replace(" ", "_")
    compact = normalized.replace("_", "")
    return (
        normalized == "id"
        or normalized.startswith("id_")
        or normalized.endswith("_id")
        or compact in {"idcliente", "clienteid", "customerid"}
    )


def parse_number(value: str) -> float:
    normalized = value.strip().replace(",", ".")
    if normalized == "":
        raise ValueError("valor vacio")
    return float(normalized)


def load_thresholds(path: Path | None) -> dict[str, float]:
    """Lee umbrales opcionales desde un CSV con columnas feature,threshold."""
    if path is None:
        return {}
    if not path.exists():
        raise ValueError(f"No existe el archivo de umbrales: {path}")

    thresholds: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["feature", "threshold"]:
            raise ValueError("El CSV de umbrales debe tener las columnas feature,threshold.")
        for row in reader:
            thresholds[row["feature"]] = parse_number(row["threshold"])
    return thresholds


def binarize_rows(
    rows: list[dict[str, str]], features: list[str], thresholds: dict[str, float] | None = None
) -> tuple[list[list[int]], dict[str, float]]:
    """Convierte variables numericas a patrones 0/1 usando medianas o umbrales dados."""
    thresholds = dict(thresholds or {})
    values_by_feature: dict[str, list[float]] = {feature: [] for feature in features}

    for row_number, row in enumerate(rows, start=1):
        for feature in features:
            try:
                values_by_feature[feature].append(parse_number(row[feature]))
            except ValueError as exc:
                raise ValueError(
                    f"Valor no numerico en fila {row_number}, variable '{feature}': {row[feature]!r}."
                ) from exc

    for feature, values in values_by_feature.items():
        thresholds.setdefault(feature, float(statistics.median(values)))

    binary_rows: list[list[int]] = []
    for row in rows:
        binary_rows.append(
            [1 if parse_number(row[feature]) >= thresholds[feature] else 0 for feature in features]
        )

    return binary_rows, thresholds


def slug_feature_name(feature: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "_" for char in feature)
    return "_".join(part for part in slug.split("_") if part)


def build_cluster_profiles(
    rows: list[dict[str, str]],
    labels: list[int],
    features: list[str],
    thresholds: dict[str, float],
) -> dict[int, dict[str, object]]:
    """Resume cada cluster con promedios originales y una etiqueta interpretable."""
    sums: dict[int, dict[str, float]] = {}
    counts: Counter[int] = Counter()

    for row, label in zip(rows, labels):
        counts[label] += 1
        sums.setdefault(label, {feature: 0.0 for feature in features})
        for feature in features:
            sums[label][feature] += parse_number(row[feature])

    profiles: dict[int, dict[str, object]] = {}
    for label in sorted(counts):
        averages = {feature: sums[label][feature] / counts[label] for feature in features}
        strongest_features = sorted(
            features,
            key=lambda feature: (-abs(averages[feature] - thresholds[feature]), feature),
        )[:2]
        label_parts = []
        for feature in strongest_features:
            direction = "alto" if averages[feature] >= thresholds[feature] else "bajo"
            label_parts.append(f"{direction}_{slug_feature_name(feature)}")
        profiles[label] = {
            "label": "_".join(label_parts) if label_parts else f"cluster_{label}",
            "averages": averages,
        }

    return profiles


def parse_rho_sensitivity(raw_values: str | None) -> list[float]:
    if raw_values is None or raw_values.strip() == "":
        return []
    values: list[float] = []
    for raw_value in raw_values.split(","):
        raw_value = raw_value.strip()
        if not raw_value:
            continue
        try:
            value = float(raw_value)
        except ValueError as exc:
            raise ValueError(f"Valor de rho invalido en --rho-sensitivity: {raw_value!r}.") from exc
        if not 0 <= value <= 1:
            raise ValueError("Todos los valores de --rho-sensitivity deben estar entre 0 y 1.")
        values.append(value)
    return values


def build_rho_sensitivity(patterns: list[list[int]], rho_values: list[float]) -> list[dict[str, object]]:
    """Calcula una mini sensibilidad del numero de clusters ante distintos rho."""
    sensitivity: list[dict[str, object]] = []
    for rho in rho_values:
        network = CarpenterGrossbergNetwork(vigilance=rho)
        labels = network.fit_predict(patterns)
        counts = Counter(labels)
        sensitivity.append(
            {
                "rho": rho,
                "clusters": len(network.prototypes),
                "distribution": dict(sorted(counts.items())),
            }
        )
    return sensitivity


def write_results(
    output_path: Path,
    rows: list[dict[str, str]],
    labels: list[int],
    id_column: str | None,
    profile_labels: dict[int, str] | None = None,
) -> None:
    if id_column and id_column not in rows[0]:
        raise ValueError(f"La columna identificadora '{id_column}' no existe en el CSV.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    base_fields = list(rows[0].keys())
    fieldnames = base_fields + ["cluster", "perfil_estimado"]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row, label in zip(rows, labels):
            output_row = dict(row)
            output_row["cluster"] = label
            output_row["perfil_estimado"] = (profile_labels or {}).get(label, f"cluster_{label}")
            writer.writerow(output_row)


def write_summary(
    summary_path: Path,
    rows: list[dict[str, str]],
    features: list[str],
    labels: list[int],
    thresholds: dict[str, float],
    network: CarpenterGrossbergNetwork,
    profiles: dict[int, dict[str, object]],
    sensitivity: list[dict[str, object]],
) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(labels)
    lines = [
        "Resumen de corrida - CarGross.py",
        "",
        f"Cantidad de clientes procesados: {len(rows)}",
        f"Cantidad de variables utilizadas: {len(features)}",
        f"Variables: {', '.join(features)}",
        f"Valor de vigilancia: {network.vigilance:.2f}",
        f"Cantidad de clusters encontrados: {len(network.prototypes)}",
        "",
        "Distribucion por cluster:",
    ]
    for cluster_id in sorted(counts):
        lines.append(f"Cluster {cluster_id}: {counts[cluster_id]} clientes")

    lines.extend(["", "Umbrales de binarizacion:"])
    for feature in features:
        lines.append(f"{feature}: {thresholds[feature]:.4f}")

    lines.extend(["", "Prototipos binarios aprendidos:"])
    for index, prototype in enumerate(network.prototypes, start=1):
        lines.append(f"Cluster {index}: {prototype}")

    lines.extend(["", "Promedios por cluster e interpretacion:"])
    for cluster_id in sorted(counts):
        profile = profiles[cluster_id]
        averages = profile["averages"]
        averages_text = ", ".join(f"{feature}={averages[feature]:.2f}" for feature in features)
        lines.append(f"Cluster {cluster_id}: {profile['label']} ({averages_text})")

    if sensitivity:
        lines.extend(
            [
                "",
                "Analisis de sensibilidad por rho:",
                "Nota: la red es incremental; los resultados tambien dependen del orden de las filas.",
            ]
        )
        for item in sensitivity:
            distribution = item["distribution"]
            distribution_text = ", ".join(
                f"C{cluster_id}={count}" for cluster_id, count in distribution.items()
            )
            lines.append(f"rho {item['rho']:.2f}: {item['clusters']} clusters ({distribution_text})")

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="CarGross.py",
        description="Red Carpenter-Grossberg clasica para agrupar filas de un CSV en clusters binarios.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Ruta del CSV de entrada.")
    parser.add_argument(
        "--features",
        help="Variables numericas separadas por coma. Ejemplo: frecuencia,monto,recencia,descuento,variedad",
    )
    parser.add_argument("--id-column", help="Columna identificadora opcional, por ejemplo id_cliente.")
    parser.add_argument("--rho", type=float, default=0.8, help="Parametro de vigilancia entre 0 y 1.")
    parser.add_argument("--thresholds", type=Path, help="CSV opcional con columnas feature,threshold.")
    parser.add_argument(
        "--rho-sensitivity",
        default="0.6,0.8,0.95",
        help="Valores de rho separados por coma para agregar una mini sensibilidad al resumen. Use '' para desactivar.",
    )
    parser.add_argument("--output", required=True, type=Path, help="CSV de salida con cluster asignado.")
    parser.add_argument("--summary", required=True, type=Path, help="TXT de resumen de corrida.")
    parser.add_argument("--min-rows", type=int, default=50, help="Cantidad minima de filas requeridas.")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        features = parse_feature_list(args.features)
        rho_sensitivity = parse_rho_sensitivity(args.rho_sensitivity)
        rows, selected_features = read_csv_dataset(args.input, features, min_rows=args.min_rows)
        thresholds = load_thresholds(args.thresholds)
        binary_rows, final_thresholds = binarize_rows(rows, selected_features, thresholds)

        network = CarpenterGrossbergNetwork(vigilance=args.rho)
        labels = network.fit_predict(binary_rows)
        profiles = build_cluster_profiles(rows, labels, selected_features, final_thresholds)
        profile_labels = {cluster_id: str(profile["label"]) for cluster_id, profile in profiles.items()}
        sensitivity = build_rho_sensitivity(binary_rows, rho_sensitivity)

        write_results(args.output, rows, labels, args.id_column, profile_labels)
        write_summary(args.summary, rows, selected_features, labels, final_thresholds, network, profiles, sensitivity)
    except ValueError as exc:
        parser.print_usage(sys.stderr)
        print(f"CarGross.py: error: {exc}", file=sys.stderr)
        return 2

    print(f"Corrida finalizada. Resultados: {args.output}")
    print(f"Resumen: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
