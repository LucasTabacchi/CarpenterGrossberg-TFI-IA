# CarpenterGrossberg_Habitos

Implementacion de una red Carpenter-Grossberg para agrupar personas segun habitos de actividad fisica.

## Categorias interpretativas

- Sedentario: persona con poca o ninguna actividad fisica.
- Levemente activo / Moderado: actividad fisica ocasional o ligera.
- Activo: entrenamiento regular varias veces por semana.
- Atleta amateur / Competitivo: entrenamiento intenso y competencias locales.
- Atleta profesional / Elite: entrenamiento muy intenso y competencias de alto nivel.

## Datasets

El proyecto usa dos fuentes:

1. `datasets/uci_har_habitos_procesado.csv`: derivado del dataset UCI Human Activity Recognition Using Smartphones. Se agrega por sujeto usando la proporcion de ventanas activas registradas por smartphone.
2. `datasets/fitbit_tracker_procesado.csv`: derivado del dataset FitBit Fitness Tracker Data de Kaggle/Bellabeat. Se agregan los archivos `dailyActivity_merged.csv` por usuario.

Fuentes de referencia:

- UCI HAR: https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones
- FitBit Fitness Tracker Data: https://www.kaggle.com/datasets/arashnic/fitbit

Para regenerarlos:

```powershell
python PrepararDatasets.py
```

El script maneja las fuentes de forma distinta porque se obtienen de forma distinta:

- UCI HAR se descarga automaticamente desde su URL publica y se guarda en `datasets/_raw/`.
- FitBit se descarga con KaggleHub usando `kagglehub.dataset_download("arashnic/fitbit")`.

Para usar la descarga con KaggleHub, instale las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Archivos generados

```text
datasets/
├── uci_har_habitos_procesado.csv
└── fitbit_tracker_procesado.csv

outputs/
├── resultados_uci_har.csv
├── resumen_uci_har.txt
├── resultados_fitbit.csv
└── resumen_fitbit.txt
```

Documentacion principal:

```text
docs/
├── Manual_HabitosCarGross.md
├── Informe_Corridas.md
└── Diccionario_Codificacion.md
```

## Variables de entrada

Las cinco variables usadas por defecto son:

- `dias_activos_semana`
- `minutos_activos_dia`
- `sesiones_entrenamiento_semana`
- `intensidad_promedio`
- `competencias_anuales`

`nivel_referencia` queda solo como referencia textual; no se usa como entrada de la red.

## Demo rapida

```powershell
python HabitosCarGross.py `
  --input datasets\uci_har_habitos_procesado.csv `
  --id-column id_persona `
  --rho 0.8 `
  --min-rows 30 `
  --output outputs\resultados_uci_har.csv `
  --summary outputs\resumen_uci_har.txt
```

```powershell
python HabitosCarGross.py `
  --input datasets\fitbit_tracker_procesado.csv `
  --id-column id_persona `
  --rho 0.8 `
  --output outputs\resultados_fitbit.csv `
  --summary outputs\resumen_fitbit.txt
```

## Pruebas

```powershell
python -m pytest tests
```
