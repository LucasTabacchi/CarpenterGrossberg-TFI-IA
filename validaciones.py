import pandas as pd


# ============================================================
# COLUMNAS REQUERIDAS
# ============================================================

COLUMNAS_REQUERIDAS = [
    "Age",
    "BMI",
    "Resting_BPM",
    "Workout_Type",
    "Workout_Frequency",
    "Session_Duration",
    "Calories_Burned",
    "Experience_Level"
]

COLUMNAS_NUMERICAS = [
    "Age",
    "BMI",
    "Resting_BPM",
    "Workout_Frequency",
    "Session_Duration",
    "Calories_Burned",
    "Experience_Level"
]


# ============================================================
# MAN - AYUDA DE USO
# ============================================================

def mostrar_man():
    """
    Muestra una ayuda de uso cuando una corrida no puede
    completarse correctamente.
    """

    print("""
============================================================
            MAN - AYUDA DE USO DE CarGross.py
============================================================

DESCRIPCION
CarGross.py implementa una red de agrupamiento adaptativo
basada en la familia Carpenter-Grossberg / Fuzzy ART.

La red procesa perfiles fitness desde archivos CSV y genera
clusters de usuarios con caracteristicas similares.

USO
    python CarGross.py

ARCHIVOS DE ENTRADA
Los datasets deben encontrarse dentro de la carpeta:

    datasets/

COLUMNAS OBLIGATORIAS
    Age
    BMI
    Resting_BPM
    Workout_Type
    Workout_Frequency
    Session_Duration
    Calories_Burned
    Experience_Level

PREPROCESAMIENTO
- Se consideran usuarios entre 20 y 40 anos.
- Workout_Type se transforma mediante One-Hot Encoding.
- Las variables numericas utilizadas por la red se
  normalizan mediante Min-Max en el intervalo [0,1].
- Experience_Level NO participa en el aprendizaje.
  Se conserva como referencia externa para analizar
  la coherencia de los clusters.

PARAMETROS PRINCIPALES
    vigilancia = 0.70
    alpha      = 0.001
    beta       = 1.0

POSIBLES PROBLEMAS
Verifique que:

1. El archivo CSV exista.
2. El archivo no este vacio.
3. El CSV contenga todas las columnas obligatorias.
4. Las variables numericas contengan valores validos.
5. No existan valores faltantes en las variables requeridas.
6. Existan registros correspondientes a edades de 20 a 40.
7. La carpeta de salida pueda ser creada o modificada.

SALIDAS
Los resultados se almacenan en:

    output/

Se generan:
- CSV con el cluster asignado a cada usuario.
- CSV con el reporte descriptivo de los clusters.

Para mas informacion consulte el Manual de Referencia.
============================================================
""")


# ============================================================
# VALIDACION DE PARAMETROS
# ============================================================

def validar_parametros(vigilancia, alpha, beta):
    """
    Comprueba que los parametros de la red se encuentren
    dentro de rangos validos.
    """

    if not 0 <= vigilancia <= 1:
        raise ValueError(
            "El parametro vigilancia debe estar entre 0 y 1."
        )

    if alpha <= 0:
        raise ValueError(
            "El parametro alpha debe ser mayor que 0."
        )

    if not 0 < beta <= 1:
        raise ValueError(
            "El parametro beta debe ser mayor que 0 "
            "y menor o igual que 1."
        )


# ============================================================
# VALIDACION DEL DATASET
# ============================================================

def validar_dataset(df):
    """
    Ejecuta las validaciones necesarias sobre el dataset
    antes de realizar cualquier preprocesamiento.
    """

    if df is None:
        raise ValueError(
            "No fue posible cargar el dataset."
        )

    if df.empty:
        raise ValueError(
            "El archivo CSV no contiene registros."
        )

    validar_columnas(df)
    validar_datos_numericos(df)
    validar_valores_faltantes(df)


def validar_columnas(df):
    """
    Comprueba que el dataset contenga todas las columnas
    necesarias para ejecutar el modelo.
    """

    faltantes = [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas obligatorias: "
            + ", ".join(faltantes)
        )


def validar_datos_numericos(df):
    """
    Comprueba que las columnas numericas contengan
    valores que puedan interpretarse como numeros.
    """

    for columna in COLUMNAS_NUMERICAS:

        conversion = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

        invalidos = (
            conversion.isna()
            & df[columna].notna()
        )

        if invalidos.any():

            cantidad = invalidos.sum()

            raise ValueError(
                f"La columna '{columna}' contiene "
                f"{cantidad} valor(es) no numerico(s)."
            )


def validar_valores_faltantes(df):
    """
    Comprueba que las columnas necesarias no contengan
    valores faltantes.
    """

    faltantes = (
        df[COLUMNAS_REQUERIDAS]
        .isnull()
        .sum()
    )

    columnas_con_faltantes = faltantes[
        faltantes > 0
    ]

    if not columnas_con_faltantes.empty:

        detalle = ", ".join(
            f"{columna}: {cantidad}"
            for columna, cantidad
            in columnas_con_faltantes.items()
        )

        raise ValueError(
            "Se encontraron valores faltantes en: "
            + detalle
        )