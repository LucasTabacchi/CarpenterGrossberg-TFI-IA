# CarpenterGrossberg_TFI

Implementacion de una red Carpenter-Grossberg para segmentar clientes desde archivos CSV.

La red trabaja con patrones binarios. Por eso `CarGross.py` toma variables numericas del CSV, calcula umbrales por mediana y transforma cada variable en 0 o 1 antes de aplicar el algoritmo.

Si no se indica `--features`, el programa infiere variables numericas y omite columnas identificadoras como `id`, `id_cliente` o `cliente_id` para evitar que un identificador distorsione la segmentacion.

## Estructura

```text
CarpenterGrossberg_TFI/
├── CarGross.py
├── README.md
├── requirements.txt
├── datasets/
│   ├── online_retail_procesado.csv
│   └── customer_shopping_behavior_procesado.csv
├── outputs/
│   ├── resultados_online_retail.csv
│   ├── resultados_customer_behavior.csv
│   ├── resumen_online_retail.txt
│   └── resumen_customer_behavior.txt
├── docs/
│   ├── Manual_CarGross.md
│   └── Informe_Corridas.md
├── referencias/
│   ├── Lau.pp5.a.11.pdf
│   └── Lau.pp12.a.14.pdf
└── tests/
    └── test_cargross.py
```

## Instalacion

Se requiere Python 3.10 o superior. El programa no necesita dependencias externas para correr.

Para ejecutar las pruebas se usa `pytest`:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests
```

## Demo rapida

```powershell
python CarGross.py `
  --input datasets\online_retail_procesado.csv `
  --features frecuencia_compra,monto_total,monto_promedio,cantidad_productos,dias_desde_ultima_compra `
  --id-column id_cliente `
  --rho 0.8 `
  --rho-sensitivity 0.6,0.8,0.95 `
  --output outputs\resultados_online_retail.csv `
  --summary outputs\resumen_online_retail.txt
```

```powershell
python CarGross.py `
  --input datasets\customer_shopping_behavior_procesado.csv `
  --features edad,monto_compra,uso_descuentos,frecuencia_compra,categoria_producto_codificada `
  --id-column id_cliente `
  --rho 0.8 `
  --rho-sensitivity 0.6,0.8,0.95 `
  --output outputs\resultados_customer_behavior.csv `
  --summary outputs\resumen_customer_behavior.txt
```

## Parametro de vigilancia

`--rho` controla que tan parecido debe ser un patron al prototipo de un cluster.

- `rho` alto: clusters mas especificos y mayor cantidad de grupos.
- `rho` bajo: clusters mas amplios y menor cantidad de grupos.

El valor usado en las demos es `0.8`.

El resumen incluye ademas una mini sensibilidad con distintos valores de `rho`, por defecto `0.6,0.8,0.95`, para observar como cambia la cantidad de clusters.

## Perfil estimado

El CSV de salida agrega `perfil_estimado` con una etiqueta interpretativa basada en los promedios originales de cada cluster y los umbrales usados para binarizar. Por ejemplo, `alto_monto_total_bajo_dias_desde_ultima_compra` indica que ese cluster queda por encima del umbral de monto total y por debajo del umbral de dias desde la ultima compra.
