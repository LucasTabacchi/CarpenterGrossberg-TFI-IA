# CarGross - Red Carpenter-Grossberg / Fuzzy ART

## Descripción

Este proyecto implementa un módulo de aprendizaje no supervisado para el agrupamiento adaptativo de perfiles fitness.

El módulo se encuentra basado en la familia de redes Carpenter-Grossberg y utiliza una implementación simplificada basada en Fuzzy ART, adecuada para trabajar con variables continuas previamente normalizadas.

El sistema analiza características biométricas y hábitos de entrenamiento para formar clusters de usuarios con perfiles similares. La cantidad de clusters no se establece previamente, sino que emerge durante el procesamiento de los datos de acuerdo con el parámetro de vigilancia.

La implementación realizada es una variante simplificada basada en Fuzzy ART y no reproduce todos los elementos del algoritmo canónico, como el complement coding.

---

## Estructura del proyecto

El proyecto se organiza de la siguiente manera:

TPI_IA/
│
├── CarGross.py
├── preprocesamiento.py
├── validaciones.py
├── preparar_datasets.py
├── requirements.txt
├── README.md
│
├── datasets/
│   ├── gym_members_exercise_tracking.csv
│   ├── fitness_dataset1_femenino.csv
│   └── fitness_dataset2_masculino.csv
│
├── metadata/
│   └── workout_type.csv
│
├── output/
│   ├── resultados_dataset1.csv
│   ├── resultados_dataset2.csv
│   ├── reporte_resultados_dataset1.csv
│   └── reporte_resultados_dataset2.csv
│
└── Docs/
    ├── Manual_de_Referencia.docx
    ├── Informe.docx
    └── Diseño_Conceptual_Tecnico.docx

### Archivos principales

- `CarGross.py`: programa principal. Ejecuta la carga de los datasets, validaciones, preprocesamiento, red neuronal y generación de resultados.
- `preprocesamiento.py`: realiza el filtro de edad, One-Hot Encoding y normalización Min-Max.
- `validaciones.py`: contiene las validaciones de parámetros y datasets, además del MAN de ayuda ante corridas incorrectas.
- `preparar_datasets.py`: genera los dos datasets de prueba a partir del dataset fuente.
- `requirements.txt`: contiene las dependencias necesarias para ejecutar el proyecto.

---

## Datasets

El proyecto utiliza dos conjuntos de prueba derivados de un mismo dataset fuente:

- `fitness_dataset1_femenino.csv`
- `fitness_dataset2_masculino.csv`

La variable `Gender` se utiliza únicamente para generar estos dos conjuntos mediante `preparar_datasets.py`. Luego es eliminada y no participa como entrada de la red.

Durante la ejecución de `CarGross.py` se consideran únicamente registros correspondientes a personas de entre 20 y 40 años.

Luego de aplicar este filtro se procesan:

- Dataset femenino: 215 registros.
- Dataset masculino: 242 registros.

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

Se realizaron pruebas con valores de vigilancia entre `0.60` y `0.90`.

Para las corridas principales se seleccionó `rho = 0.70`, ya que dentro de las configuraciones evaluadas presentó un equilibrio adecuado entre la coherencia descriptiva de los agrupamientos y la fragmentación producida.

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

## Resultados esperados de las corridas principales

Con la configuración:

    vigilancia = 0.70
    alpha = 0.001
    beta = 1.0

se obtuvieron los siguientes resultados:

- Dataset femenino: 215 registros procesados y 44 clusters.
- Dataset masculino: 242 registros procesados y 45 clusters.

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