# Diccionario de codificacion - CarGross.py

## Columnas de referencia

| Columna | Significado | Usada por la red |
|---|---|---|
| `id_persona` | Identificador de la persona o sujeto. | No |
| `fuente` | Origen del registro: UCI HAR o FitBit. | No |
| `nivel_referencia` | Etiqueta conocida o referencia del dataset. | No |

## Variables usadas por la red

| Columna | Significado | Usada por la red |
|---|---|---|
| `dias_activos_semana` | Dias estimados con actividad fisica en una semana. | Si |
| `minutos_activos_dia` | Minutos diarios promedio de actividad. En FitBit surge de minutos livianos + moderados + intensos. | Si |
| `sesiones_entrenamiento_semana` | Sesiones semanales estimadas desde dias con pasos altos o minutos moderados/intensos. | Si |
| `intensidad_promedio` | Intensidad estimada de 1 a 5. En FitBit pondera minutos livianos, moderados e intensos. | Si |
| `competencias_anuales` | Competencias o eventos deportivos anuales. En FitBit queda en 0 porque el dataset no lo registra. | Si |

## Binarizacion

Cada variable numerica se transforma a patron binario:

```text
si valor >= umbral -> 1
si valor <  umbral -> 0
```

Si no se entrega un CSV de umbrales, el umbral de cada variable es su mediana en el dataset de entrada.

## Interpretacion posterior

La red no aprende etiquetas supervisadas. Primero descubre clusters y despues `HabitosCarGross.py` calcula los promedios originales de cada cluster para asignar una de las cinco categorias: Sedentario, Levemente activo / Moderado, Activo, Atleta amateur / Competitivo o Atleta profesional / Elite.
