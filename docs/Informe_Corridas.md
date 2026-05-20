# Informe de corridas - HabitosCarGross.py

## Datasets

### Dataset 1: UCI HAR Smartphones

Archivo procesado: `datasets/uci_har_habitos_procesado.csv`.

El dataset original registra ventanas de actividad medidas por smartphone. Para adaptarlo a la consigna de personas segun habitos, se agregaron las ventanas por sujeto y se derivaron cinco variables numericas compatibles con la red.

Variables derivadas:

- `dias_activos_semana`: estimacion semanal basada en la proporcion de ventanas activas del sujeto.
- `minutos_activos_dia`: estimacion diaria a partir de la proporcion de actividad y de la presencia de caminata o escaleras.
- `sesiones_entrenamiento_semana`: aproximacion derivada de ventanas de caminata y escaleras.
- `intensidad_promedio`: escala 1 a 5 calculada desde el porcentaje de actividad y la participacion de escaleras.
- `competencias_anuales`: queda en 0 porque UCI HAR no registra competencias ni eventos deportivos.

### Dataset 2: FitBit Fitness Tracker Data

Archivo procesado: `datasets/fitbit_tracker_procesado.csv`.

El dataset contiene exportaciones Fitabase de usuarios Fitbit. Para conservar la unidad "persona", se agregaron los archivos `dailyActivity_merged.csv` por `Id`.

Variables derivadas:

- `dias_activos_semana`: dias activos promedio por semana observada. Un dia cuenta como activo si tiene al menos 20 minutos activos o 3000 pasos.
- `minutos_activos_dia`: promedio diario de `VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes`.
- `sesiones_entrenamiento_semana`: dias semanales con al menos 10 minutos moderados/intensos o 7500 pasos.
- `intensidad_promedio`: escala 1 a 5 calculada como promedio ponderado de minutos livianos, moderados e intensos.
- `competencias_anuales`: queda en 0 porque FitBit Fitness Tracker Data no registra competencias ni eventos deportivos.

## Corridas generadas

### UCI HAR Smartphones

- Entrada: `datasets/uci_har_habitos_procesado.csv`
- Salida: `outputs/resultados_uci_har.csv`
- Resumen: `outputs/resumen_uci_har.txt`
- Valor de vigilancia: `rho = 0.8`

La corrida procesa 30 sujetos agregados desde UCI HAR.

Resultado de la corrida:

- Cantidad de clusters encontrados: 3.
- Cluster 1: 21 personas - Activo.
- Cluster 2: 4 personas - Activo.
- Cluster 3: 5 personas - Activo.

Umbrales de binarizacion:

- `dias_activos_semana`: 3.7850
- `minutos_activos_dia`: 63.6450
- `sesiones_entrenamiento_semana`: 2.7000
- `intensidad_promedio`: 2.8500
- `competencias_anuales`: 0.0000

Prototipos aprendidos:

- Cluster 1: `[0, 0, 0, 0, 1]`
- Cluster 2: `[0, 0, 1, 1, 1]`
- Cluster 3: `[1, 1, 1, 1, 1]`

Interpretacion: los tres clusters quedan dentro de la categoria `Activo`. Esto ocurre porque UCI HAR, una vez agregado por sujeto, contiene personas que participaron en actividades medidas por smartphone y no representa una muestra amplia de personas sedentarias, moderadas, amateurs y elite. La red igualmente separa subgrupos internos segun mayor o menor actividad estimada.

Analisis de sensibilidad:

- `rho = 0.60`: 2 clusters.
- `rho = 0.80`: 3 clusters.
- `rho = 0.95`: 3 clusters.

### FitBit Fitness Tracker Data

- Entrada: `datasets/fitbit_tracker_procesado.csv`
- Salida: `outputs/resultados_fitbit.csv`
- Resumen: `outputs/resumen_fitbit.txt`
- Valor de vigilancia: `rho = 0.8`

La corrida procesa 35 usuarios FitBit y encuentra 8 clusters. La interpretacion posterior queda distribuida asi:

- Activo: 18 personas.
- Atleta amateur / Competitivo: 17 personas.

Resultado por cluster:

- Cluster 1: 9 personas - Activo.
- Cluster 2: 8 personas - Activo.
- Cluster 3: 3 personas - Atleta amateur / Competitivo.
- Cluster 4: 4 personas - Atleta amateur / Competitivo.
- Cluster 5: 1 persona - Activo.
- Cluster 6: 7 personas - Atleta amateur / Competitivo.
- Cluster 7: 2 personas - Atleta amateur / Competitivo.
- Cluster 8: 1 persona - Atleta amateur / Competitivo.

Umbrales de binarizacion:

- `dias_activos_semana`: 6.7700
- `minutos_activos_dia`: 232.5300
- `sesiones_entrenamiento_semana`: 4.4400
- `intensidad_promedio`: 1.8300
- `competencias_anuales`: 0.0000

Prototipos aprendidos:

- Cluster 1: `[0, 0, 0, 0, 1]`
- Cluster 2: `[0, 0, 0, 1, 1]`
- Cluster 3: `[1, 0, 0, 0, 1]`
- Cluster 4: `[0, 1, 0, 0, 1]`
- Cluster 5: `[0, 1, 0, 1, 1]`
- Cluster 6: `[1, 1, 1, 0, 1]`
- Cluster 7: `[0, 0, 1, 1, 1]`
- Cluster 8: `[1, 0, 1, 1, 1]`

Interpretacion: FitBit produce una separacion mas rica que UCI HAR para esta consigna porque contiene registros diarios de actividad, pasos y minutos por intensidad. La red no encuentra perfiles sedentarios en esta muestra procesada, pero si diferencia usuarios `Activos` de usuarios con comportamiento compatible con `Atleta amateur / Competitivo`.

Analisis de sensibilidad:

- `rho = 0.60`: 5 clusters.
- `rho = 0.80`: 8 clusters.
- `rho = 0.95`: 9 clusters.

## Criterio de interpretacion

La red genera clusters no supervisados. Luego cada cluster se resume con promedios por variable y se asigna un nivel de habito estimado mediante un puntaje ponderado de actividad, entrenamiento, intensidad y competencia.
