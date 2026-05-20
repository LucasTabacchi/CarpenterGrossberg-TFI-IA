# Manual de referencia - CarGross.py

## Alcance

`CarGross.py` implementa una red Carpenter-Grossberg clasica y didactica para agrupar personas segun habitos de actividad fisica.

El programa:

- lee archivos CSV procesados;
- valida cantidad minima de filas;
- usa variables numericas indicadas por el usuario o inferidas automaticamente;
- binariza variables mediante umbrales;
- aplica el algoritmo Carpenter-Grossberg;
- genera un CSV con clusters, perfil interpretativo y nivel de habito estimado;
- genera un resumen de corrida con sensibilidad por `rho`;
- informa errores de uso con ayuda por consola.

El proyecto tambien incluye `PrepararDatasets.py`, que descarga y procesa los datasets originales:

- UCI Human Activity Recognition Using Smartphones;
- FitBit Fitness Tracker Data de Kaggle.

## Categorias interpretativas

La red no aprende estas categorias como etiquetas supervisadas. Primero genera clusters no supervisados y despues el programa interpreta los promedios de cada cluster.

Categorias usadas:

- `Sedentario`: poca o ninguna actividad fisica.
- `Levemente activo / Moderado`: actividad fisica ocasional o ligera.
- `Activo`: entrenamiento regular varias veces por semana.
- `Atleta amateur / Competitivo`: entrenamiento intenso y participacion competitiva local o equivalente.
- `Atleta profesional / Elite`: entrenamiento muy intenso y competencia de alto nivel o equivalente.

## Limitaciones

- La version clasica usa patrones binarios 0/1.
- Las variables originales se convierten a 0/1 por mediana o por umbrales dados.
- El resultado depende del orden de las filas.
- El resultado depende del valor de vigilancia `rho`.
- Las categorias de habito son interpretaciones posteriores; la red solo devuelve clusters.
- Los datasets no registran todas las dimensiones humanas del habito fisico. Por ejemplo, UCI HAR no registra competencias y FitBit tampoco registra eventos deportivos formales.

## Instalacion

Requisito: Python 3.10 o superior.

```powershell
cd C:\Users\lucas\Documents\Playground\CarpenterGrossberg_Habitos
python --version
python -m pip install -r requirements.txt
```

## Preparacion de datasets

Para descargar y procesar los datasets:

```powershell
python PrepararDatasets.py
```

El script genera:

```text
datasets/uci_har_habitos_procesado.csv
datasets/fitbit_tracker_procesado.csv
```

### UCI HAR Smartphones

Se descarga desde la URL publica del repositorio UCI. El ZIP queda en `datasets/_raw/uci_har.zip` y se extrae en `datasets/_raw/uci_har/`.

El procesamiento agrupa ventanas por sujeto usando:

- `subject_train.txt`
- `subject_test.txt`
- `y_train.txt`
- `y_test.txt`

### FitBit Fitness Tracker Data

Se descarga con:

```python
kagglehub.dataset_download("arashnic/fitbit")
```

El procesamiento busca archivos `dailyActivity_merged.csv`, agrupa por `Id` y genera un registro por usuario.

## Formato del CSV procesado

Los CSV procesados tienen encabezados y al menos estas columnas:

```text
id_persona,fuente,nivel_referencia,dias_activos_semana,minutos_activos_dia,sesiones_entrenamiento_semana,intensidad_promedio,competencias_anuales
```

Columnas de referencia:

- `id_persona`: identificador del sujeto o usuario.
- `fuente`: origen del registro.
- `nivel_referencia`: referencia textual; no entra a la red.

Variables usadas por la red:

- `dias_activos_semana`
- `minutos_activos_dia`
- `sesiones_entrenamiento_semana`
- `intensidad_promedio`
- `competencias_anuales`

## Uso

Corrida con UCI HAR:

```powershell
python HabitosCarGross.py `
  --input datasets\uci_har_habitos_procesado.csv `
  --id-column id_persona `
  --rho 0.8 `
  --min-rows 30 `
  --output outputs\resultados_uci_har.csv `
  --summary outputs\resumen_uci_har.txt
```

Corrida con FitBit:

```powershell
python HabitosCarGross.py `
  --input datasets\fitbit_tracker_procesado.csv `
  --id-column id_persona `
  --rho 0.8 `
  --output outputs\resultados_fitbit.csv `
  --summary outputs\resumen_fitbit.txt
```

## Parametros de HabitosCarGross.py

- `--input`: CSV de entrada.
- `--features`: variables numericas separadas por coma. Si se omite, se priorizan las variables de habito.
- `--id-column`: columna identificadora opcional, por ejemplo `id_persona`.
- `--rho`: parametro de vigilancia entre 0 y 1.
- `--thresholds`: CSV opcional con columnas `feature,threshold`.
- `--rho-sensitivity`: valores de rho separados por coma para agregar una mini sensibilidad al resumen. Por defecto, `0.6,0.8,0.95`. Use `""` para desactivar.
- `--output`: CSV de resultados.
- `--summary`: TXT de resumen.
- `--min-rows`: minimo de filas requeridas. Por defecto, 50.

## Parametros de PrepararDatasets.py

- `--datasets-dir`: carpeta donde se escriben los CSV procesados. Por defecto, `datasets`.
- `--work-dir`: carpeta auxiliar para guardar y extraer UCI HAR. Por defecto, `datasets/_raw`.
- `--skip-uci`: evita descargar/procesar UCI HAR y procesa solo FitBit.

## Salida esperada

El CSV de salida conserva las columnas originales y agrega:

- `cluster`: numero de cluster asignado.
- `perfil_estimado`: etiqueta interpretativa basada en los promedios originales del cluster y los umbrales de binarizacion.
- `nivel_habito_estimado`: una de las cinco categorias interpretativas.

El resumen incluye:

- cantidad de personas procesadas;
- variables usadas;
- valor de vigilancia;
- cantidad de clusters;
- distribucion por cluster;
- umbrales de binarizacion;
- prototipos binarios aprendidos;
- promedios por cluster e interpretacion;
- sensibilidad de cantidad de clusters ante distintos valores de `rho`.

## FAQ

**1. Por que hay que binarizar los datos?**

Porque la version clasica del algoritmo Carpenter-Grossberg usada en el trabajo opera con patrones binarios.

**2. Que pasa si cambio `rho`?**

Si sube `rho`, la red exige coincidencias mas fuertes y suele crear mas clusters. Si baja `rho`, agrupa patrones mas diferentes.

**3. El nivel de habito estimado es una etiqueta real del dataset?**

No. Es una interpretacion posterior. La red devuelve clusters; luego el programa resume los promedios de actividad de cada cluster y asigna una categoria como `Activo` o `Atleta amateur / Competitivo`.

**4. Por que UCI HAR queda todo como Activo?**

Porque UCI HAR contiene sujetos realizando actividades medidas por smartphone. Al agregarlo por sujeto, no representa una muestra amplia de sedentarismo, actividad ligera y elite; aun asi, la red separa subgrupos internos.

**5. Por que FitBit no tiene competencias anuales?**

Porque el dataset FitBit registra actividad diaria, pasos y minutos por intensidad, pero no registra competencias deportivas formales. Por eso `competencias_anuales` queda en 0.
