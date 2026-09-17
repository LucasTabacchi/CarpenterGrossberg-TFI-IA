import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# ============================================================
# CARGA DEL DATASET
# ============================================================

def cargar_datos(ruta_archivo):
    """
    Carga un archivo CSV y devuelve un DataFrame.

    Esta funcion solamente realiza la lectura.
    Las validaciones se ejecutan posteriormente,
    antes de utilizar las columnas del dataset.
    """

    try:

        df = pd.read_csv(ruta_archivo)

        print(
            f"Archivo cargado exitosamente. "
            f"Total registros: {len(df)}"
        )

        return df

    except FileNotFoundError:

        raise FileNotFoundError(
            f"No se encontro el archivo: {ruta_archivo}"
        )

    except pd.errors.EmptyDataError:

        raise ValueError(
            "El archivo CSV esta vacio."
        )

    except pd.errors.ParserError:

        raise ValueError(
            "El archivo no posee un formato CSV valido."
        )

    except UnicodeDecodeError:

        raise ValueError(
            "No fue posible interpretar la codificacion "
            "del archivo CSV."
        )


# ============================================================
# FILTRO DEL ALCANCE
# ============================================================

def filtrar_por_edad(df):
    """
    Filtra el dataset para conservar solamente personas
    entre 20 y 40 anos, de acuerdo con el alcance definido
    para el proyecto.
    """

    dentro_del_rango = df["Age"].between(
        20,
        40,
        inclusive="both"
    )

    excluidos = (~dentro_del_rango).sum()

    df_filtrado = df[
        dentro_del_rango
    ].copy()

    print(
        "Registros excluidos por edad fuera "
        f"de 20 a 40 anos: {excluidos}"
    )

    print(
        "Registros dentro del alcance de "
        f"20 a 40 anos: {len(df_filtrado)}"
    )

    if df_filtrado.empty:

        raise ValueError(
            "No quedaron registros dentro del rango "
            "de edad definido (20 a 40 anos)."
        )

    return df_filtrado


# ============================================================
# PREPROCESAMIENTO PARA LA RED
# ============================================================

def preprocesar_datos(df):
    """
    Prepara los datos que ingresaran a la red.

    - Workout_Type se transforma mediante One-Hot Encoding.
    - Las variables numericas se normalizan mediante
      Min-Max al intervalo [0,1].
    - Experience_Level se conserva como referencia externa,
      pero NO se utiliza como entrada de la red.
    """

    # --------------------------------------------------------
    # Guardamos Experience_Level antes de preparar
    # las variables que ingresaran a la red.
    # --------------------------------------------------------

    niveles_experiencia = (
        df["Experience_Level"]
        .copy()
        .values
    )

    # --------------------------------------------------------
    # Variables numericas utilizadas por la red
    # --------------------------------------------------------

    variables_numericas = [
        "Age",
        "BMI",
        "Resting_BPM",
        "Workout_Frequency",
        "Session_Duration",
        "Calories_Burned"
    ]

    df_red = df[
        variables_numericas + ["Workout_Type"]
    ].copy()

    # --------------------------------------------------------
    # ONE-HOT ENCODING DE WORKOUT_TYPE
    # --------------------------------------------------------

    df_red = pd.get_dummies(
        df_red,
        columns=["Workout_Type"],
        dtype=float
    )

    # --------------------------------------------------------
    # NORMALIZACION MIN-MAX
    # --------------------------------------------------------

    scaler = MinMaxScaler()

    df_red[variables_numericas] = (
        scaler.fit_transform(
            df_red[variables_numericas]
        )
    )

    return (
        df_red.values,
        df_red.columns,
        niveles_experiencia
    )