# Diccionario de codificacion de datasets

Este documento registra las columnas codificadas o derivadas usadas en los CSV procesados del proyecto.

Importante: el repositorio contiene los CSV ya procesados, pero no incluye el script original que genero esos CSV desde las fuentes crudas. Por eso, cuando el mapeo texto-original -> codigo no puede recuperarse de los archivos actuales, se marca como "no recuperable desde el repo".

## Dataset: online_retail_procesado.csv

Archivo: `datasets/online_retail_procesado.csv`

### Variables usadas por la red

| Columna procesada | Origen conceptual | Tipo | Codificacion / calculo | Usada por la red |
|---|---|---|---|---|
| `frecuencia_compra` | `InvoiceNo` agrupado por `CustomerID` | Numerica derivada | Cantidad de facturas/compras distintas por cliente. | Si |
| `monto_total` | `Quantity` y `UnitPrice` agrupados por `CustomerID` | Numerica derivada | `sum(Quantity * UnitPrice)` por cliente. | Si |
| `monto_promedio` | `monto_total` y `frecuencia_compra` | Numerica derivada | `monto_total / frecuencia_compra`. | Si |
| `cantidad_productos` | `Quantity` agrupado por `CustomerID` | Numerica derivada | `sum(Quantity)` por cliente. | Si |
| `dias_desde_ultima_compra` | `InvoiceDate` agrupado por `CustomerID` | Numerica derivada | Diferencia entre fecha de referencia y ultima compra del cliente. | Si |

### Variables disponibles pero no usadas como entrada principal

| Columna procesada | Codigos / valores visibles | Significado | Usada por la red |
|---|---|---|---|
| `id_cliente` | `1001` a `1060` | Identificador generado/renombrado del cliente. No debe usarse para segmentar. | No |
| `perfil_referencia` | `frecuente`, `alto_valor`, `descuentos`, `ocasional`, `riesgo_abandono` | Etiqueta de referencia para interpretar la corrida. No es entrada del algoritmo. | No |
| `uso_descuentos` | `0`, `1` | Variable binaria disponible. `0` indica no/menor uso de descuentos; `1` indica uso de descuentos. | No |
| `variedad_productos` | Numeros enteros | Cantidad de productos distintos comprados, equivalente conceptual a `count_distinct(StockCode)`. | No |

### Observacion sobre codificacion

En este dataset, las variables que entran a la red son principalmente metricas numericas derivadas de transacciones. No hay un diccionario categorico principal usado por la red. La transformacion clave fue pasar de lineas de factura a una tabla resumida por cliente.

## Dataset: customer_shopping_behavior_procesado.csv

Archivo: `datasets/customer_shopping_behavior_procesado.csv`

### Variables usadas por la red

| Columna procesada | Origen conceptual | Codigos / valores visibles | Codificacion / calculo | Usada por la red |
|---|---|---|---|---|
| `edad` | `Age` | Valores numericos | Se conserva como numero. | Si |
| `monto_compra` | `Purchase Amount (USD)` | Valores numericos | Se conserva como monto numerico. | Si |
| `uso_descuentos` | `Discount Applied` | `0`, `1` | Codificacion binaria: `0` = no usa descuento, `1` = usa descuento. | Si |
| `frecuencia_compra` | `Frequency of Purchases` y/o `Previous Purchases` | `0` a `8` | Frecuencia adaptada a escala numerica. El mapeo exacto desde texto original no es recuperable desde el repo. | Si |
| `categoria_producto_codificada` | `Category` | `1`, `2`, `3`, `4`, `5` | Categoria de producto codificada como numero. El diccionario exacto categoria -> codigo no es recuperable desde el repo. | Si |

### Variables codificadas pero no usadas como entrada principal

| Columna procesada | Origen conceptual | Codigos / valores visibles | Codificacion / calculo | Usada por la red |
|---|---|---|---|---|
| `metodo_pago_codificado` | `Payment Method` | `1`, `2`, `3` | Metodo de pago codificado como numero. El diccionario exacto metodo -> codigo no es recuperable desde el repo. | No |
| `temporada_codificada` | `Season` | `1`, `2`, `3`, `4` | Temporada codificada como numero. El diccionario exacto temporada -> codigo no es recuperable desde el repo. | No |

### Variables disponibles para referencia

| Columna procesada | Codigos / valores visibles | Significado | Usada por la red |
|---|---|---|---|
| `id_cliente` | `2001` a `2060` | Identificador generado/renombrado del cliente. No debe usarse para segmentar. | No |
| `perfil_referencia` | `joven_descuentos`, `premium`, `estacional`, `regular`, `baja_actividad` | Etiqueta de referencia para interpretar la corrida. No es entrada del algoritmo. | No |

## Paso posterior: binarizacion

Despues de estas codificaciones, `CarGross.py` vuelve a transformar cada variable usada por la red a un patron binario.

La regla es:

```text
si valor >= umbral -> 1
si valor <  umbral -> 0
```

Por defecto, el umbral es la mediana de cada columna seleccionada. Por eso una categoria codificada como `1`, `2`, `3`, `4`, `5` no entra a la red con esos cinco valores: primero se compara contra el umbral y termina como `0` o `1`.
