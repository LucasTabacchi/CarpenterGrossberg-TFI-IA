# CarGross - Red Carpenter-Grossberg / Fuzzy ART

## Descripción

Este proyecto implementa un módulo de aprendizaje no supervisado para el agrupamiento adaptativo de perfiles fitness.

El módulo se encuentra basado en la familia de redes Carpenter-Grossberg y utiliza una implementación simplificada basada en Fuzzy ART, adecuada para trabajar con variables continuas previamente normalizadas.

El sistema analiza características biométricas y hábitos de entrenamiento para formar clusters de usuarios con perfiles similares. La cantidad de clusters no se establece previamente, sino que emerge durante el procesamiento de los datos de acuerdo con el parámetro de vigilancia.

La implementación realizada es una variante simplificada basada en Fuzzy ART y no reproduce todos los elementos del algoritmo canónico, como el complement coding.

---

## Estructura del proyecto

El proyecto se organiza de la siguiente manera:

```text
TPI_IA/
│
├── CarGross.py
├── preprocesamiento.py
├── validaciones.py
├── preparar_datasets.py
├── probar_vigilancias.py
├── requirements.txt
├── README.md
│
├── datasets/
│   ├── gym_members_exercise_tracking.csv
│   ├── fitness_dataset1_femenino.csv
│   ├── fitness_dataset2_masculino.csv
│   └── reserva/
│       └── fitness_masculino_reserva.csv
│
├── metadata/
│   └── workout_type.csv
│
├── output/
│   ├── resultados_dataset1.csv
│   ├── resultados_dataset2.csv
│   ├── reporte_resultados_dataset1.csv
│   ├── reporte_resultados_dataset2.csv
│   └── pruebas_vigilancia/
│       ├── resumen_vigilancias.csv
│       └── rho_060/ ... rho_090/
│
└── Docs/
    ├── Manual_de_Referencia.docx
    ├── Informe.docx
```

### Archivos principales

- `CarGross.py`: programa principal. Ejecuta la carga de los datasets, validaciones, preprocesamiento, red neuronal y generación de resultados.
- `preprocesamiento.py`: realiza el filtro de edad, One-Hot Encoding y normalización Min-Max.
- `validaciones.py`: contiene las validaciones de parámetros y datasets, además del MAN de ayuda ante corridas incorrectas.
- `preparar_datasets.py`: genera los datasets balanceados y conserva los registros masculinos no seleccionados en reserva.
- `probar_vigilancias.py`: ejecuta las 14 pruebas experimentales y guarda resultados independientes y un resumen comparativo.
- `requirements.txt`: contiene las dependencias necesarias para ejecutar el proyecto.

---

## Datasets

El proyecto utiliza dos conjuntos de prueba derivados de un mismo dataset fuente:

- `fitness_dataset1_femenino.csv`
- `fitness_dataset2_masculino.csv`

La variable `Gender` se utiliza únicamente para generar estos dos conjuntos mediante `preparar_datasets.py`. Luego se elimina de los dos CSV de entrada y no participa en la red.

El dataset fuente contiene 462 registros femeninos y 511 masculinos. Para balancear los tamaños iniciales, se seleccionan aleatoriamente 462 registros masculinos mediante `random_state=42` (semilla fija para reproducibilidad). Los 49 registros masculinos no seleccionados se conservan en `datasets/reserva/fitness_masculino_reserva.csv` y **no se utilizan en las corridas**. No se fuerza la igualdad por tipo de entrenamiento.

Durante la ejecución de `CarGross.py` se consideran únicamente registros correspondientes a personas de entre 20 y 40 años.

Luego de aplicar este filtro se procesan:

- Dataset femenino: 215 registros.
- Dataset masculino: 221 registros.

Las variables utilizadas como entrada de la red son:

- `Age`
- `BMI`
- `Resting_BPM`
- `Workout_Type`
- `Workout_Frequency`
- `Session_Duration`
- `Calories_Burned`

La variable `Experience_Level` se conserva como referencia externa para el análisis posterior de los clusters, pero no participa en el aprendizaje de la red.

---

## Metadata

El proyecto incluye el archivo:

`metadata/workout_type.csv`

Este archivo funciona como metadata descriptiva asociada a la variable categórica `Workout_Type`.

Contiene:

- `Workout_Type_ID`
- `Workout_Name`
- `Description`

Las categorías documentadas son:

- HIIT
- Cardio
- Strength
- Yoga

Esta metadata tiene una finalidad descriptiva y facilita la interpretación de los datos. No constituye una entrada adicional de la red ni interviene directamente en la formación de los clusters.

Durante el preprocesamiento, `Workout_Type` se obtiene del dataset principal y se transforma mediante One-Hot Encoding.

---

## Preprocesamiento

Antes de ingresar los datos a la red se realizan las siguientes operaciones:

1. Validación de la estructura y contenido del archivo CSV.
2. Filtrado de registros para conservar edades entre 20 y 40 años.
3. Separación de `Experience_Level` como referencia externa.
4. Transformación de `Workout_Type` mediante One-Hot Encoding.
5. Normalización de las variables numéricas mediante Min-Max al intervalo `[0,1]`.

---

## Requisitos

El módulo fue desarrollado y probado utilizando:

- Python 3.9.6
- NumPy 2.0.2
- Pandas 2.3.3
- Scikit-learn 1.6.1

Las dependencias directas se encuentran especificadas en `requirements.txt`.

---

## Instalación

Se recomienda crear un entorno virtual antes de instalar las dependencias.

### Crear el entorno virtual

En Windows:

    python -m venv entorno

### Activar el entorno

En CMD:

    entorno\Scripts\activate

En PowerShell:

    .\entorno\Scripts\Activate.ps1

### Instalar las dependencias

Con el entorno activado, ejecutar:

    pip install -r requirements.txt

---

## Ejecución

Para ejecutar el módulo principal, ubicarse en la carpeta raíz del proyecto y ejecutar:

    python CarGross.py

El programa procesa automáticamente los dos datasets definidos dentro de la carpeta `datasets/`.

No es necesario indicar manualmente los archivos durante las demostraciones incluidas en este proyecto.

---

## Parámetros utilizados

Las corridas principales utilizan la siguiente configuración:

- Vigilancia (`rho`): `0.70`
- Alpha (`alpha`): `0.001`
- Beta (`beta`): `1.0`

El parámetro de vigilancia determina el grado mínimo de coincidencia requerido para que un patrón pueda incorporarse a un cluster existente.

Se realizaron **14 corridas**: siete valores de vigilancia (`0.60`, `0.65`, `0.70`, `0.75`, `0.80`, `0.85` y `0.90`) para cada uno de los dos datasets definitivos.

Para las corridas principales se seleccionó `rho = 0.70` como configuración común de compromiso. Con este valor se obtuvieron 44 clusters femeninos (coherencia descriptiva por `Workout_Type` de 95,81 %) y 53 masculinos (93,21 %). Con `rho = 0.75` se obtuvo mayor coherencia (97,21 % y 97,74 %), especialmente favorable para el conjunto masculino; sin embargo, en el femenino aumentaron los clusters de tres integrantes o menos de 12 a 22. No se afirma que `0.70` sea universalmente óptimo.

Los valores `alpha = 0.001` y `beta = 1.0` se mantuvieron constantes durante estas pruebas y no se presentan como valores óptimos universales.

---

## Resultados

Los archivos generados se almacenan automáticamente en la carpeta:

`output/`

Para cada dataset se generan dos tipos de archivos.

### Resultados individuales

- `resultados_dataset1.csv`
- `resultados_dataset2.csv`

Estos archivos conservan los registros procesados e incorporan la columna:

`Cluster_Asignado`

que indica el cluster asignado por la red a cada usuario.

### Reportes descriptivos

- `reporte_resultados_dataset1.csv`
- `reporte_resultados_dataset2.csv`

Estos archivos resumen la composición de cada cluster e incluyen:

- cantidad de usuarios;
- Workout_Type predominante;
- distribución de Workout_Type;
- Experience_Level predominante;
- distribución de Experience_Level;
- promedios de variables biométricas y de entrenamiento.

`Experience_Level` se utiliza únicamente para la interpretación posterior de los resultados y no participa en la formación de los clusters.

---

## Preparación y reproducción de los experimentos

Para regenerar los datasets a partir del CSV fuente, ejecutar desde la raíz del proyecto:

```powershell
python preparar_datasets.py
```

Este paso reproduce la selección aleatoria balanceada con semilla `42`. Después, ejecutar las pruebas de vigilancia:

```powershell
python probar_vigilancias.py
```

El script procesa ambos datasets para cada uno de los siete valores de vigilancia y guarda los archivos de cada corrida en `output/pruebas_vigilancia/`, organizados por vigilancia. El resumen conjunto queda en `output/pruebas_vigilancia/resumen_vigilancias.csv`. Las pruebas no reemplazan los CSV principales generados por `CarGross.py`.

El indicador de coherencia por `Workout_Type` se calcula a posteriori como la proporción de registros cuya actividad coincide con la actividad predominante de su cluster. Es una **medida descriptiva**, no una exactitud de clasificación supervisada. `Experience_Level` también se utiliza solo para interpretación externa.

---

## Resultados esperados de las corridas principales

Con la configuración:

    vigilancia = 0.70
    alpha = 0.001
    beta = 1.0

se obtuvieron los siguientes resultados:

- Dataset femenino: 215 registros procesados y 44 clusters.
- Dataset masculino: 221 registros procesados y 53 clusters.

Debido al carácter incremental del algoritmo, los resultados deben interpretarse dentro de las condiciones de preprocesamiento, parámetros y orden de presentación utilizados en este proyecto.

---

## Manejo de errores

El módulo incorpora validaciones para detectar, entre otros casos:

- archivos inexistentes;
- archivos CSV vacíos;
- columnas obligatorias faltantes;
- valores no numéricos en variables numéricas;
- valores faltantes;
- ausencia de registros dentro del rango de edad definido;
- parámetros de red fuera de los rangos permitidos;
- problemas de acceso o escritura de archivos.

Ante una corrida que no puede completarse correctamente, el programa muestra un MAN con información básica de uso, requisitos del dataset, parámetros y posibles problemas.

---

## Documentación

Para una explicación detallada del funcionamiento, instalación, alcance, limitaciones y demostración del módulo, consultar el Manual de Referencia incluido en la carpeta `Docs/`.

El Informe de Resultados contiene las corridas realizadas sobre ambos conjuntos de prueba, el análisis del parámetro de vigilancia y la evaluación e interpretación de los clusters obtenidos.

El documento de Diseño Conceptual y Técnico se conserva como documentación complementaria del proceso de diseño del sistema.

---

## Alcance

El proyecto fue desarrollado con fines académicos para estudiar la aplicación de redes de la familia Carpenter-Grossberg al agrupamiento adaptativo de perfiles fitness.

El análisis se limita al alcance y a los conjuntos de datos definidos para este trabajo.

El módulo no constituye un sistema de diagnóstico médico ni realiza recomendaciones clínicas o deportivas.
