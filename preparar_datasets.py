import pandas as pd
import os


def preparar_datasets_por_genero(ruta_csv_original):
    print("Iniciando la preparación de los datasets...")

    try:
        df = pd.read_csv(ruta_csv_original)
        print(f"Dataset original cargado. Total de registros: {len(df)}")
    except FileNotFoundError:
        print("Error: No se encontró el archivo original.")
        return

    # Renombrar las columnas originales
    df.rename(columns={
        'Workout_Frequency (days/week)': 'Workout_Frequency',
        'Session_Duration (hours)': 'Session_Duration'
    }, inplace=True)

    # Variables seleccionadas en el diseño técnico
    columnas_utiles = [
        'Age', 'BMI', 'Resting_BPM', 'Workout_Type',
        'Workout_Frequency', 'Session_Duration',
        'Calories_Burned', 'Experience_Level', 'Gender'
    ]

    # Seleccionar columnas y eliminar filas incompletas
    # El filtro de edad se aplica posteriormente en preprocesamiento.py
    df_filtrado = df[columnas_utiles].dropna().copy()

    # Separar registros por género
    df_femenino = df_filtrado[
        df_filtrado['Gender'] == 'Female'
    ].copy()

    df_masculino = df_filtrado[
        df_filtrado['Gender'] == 'Male'
    ].copy()

    print("\n=== DISTRIBUCIÓN ORIGINAL ===")
    print(f"Mujeres: {len(df_femenino)}")
    print(f"Hombres: {len(df_masculino)}")

    # BALANCEO ALEATORIO
    # Seleccionar tantos hombres como mujeres,
    # manteniendo una semilla fija para reproducibilidad.

    cantidad_objetivo = len(df_femenino)

    if len(df_masculino) < cantidad_objetivo:
        print("Error: No hay suficientes registros masculinos para balancear.")
        return

    df_masculino_balanceado = df_masculino.sample(
        n=cantidad_objetivo,
        random_state=42
    ).copy()

    # Reservar los registros masculinos no seleccionados
    df_masculino_reserva = df_masculino.drop(
        index=df_masculino_balanceado.index
    ).copy()

    print("\n=== DISTRIBUCIÓN DESPUÉS DEL BALANCEO ===")
    print(f"Mujeres: {len(df_femenino)}")
    print(f"Hombres seleccionados: {len(df_masculino_balanceado)}")
    print(f"Hombres reservados: {len(df_masculino_reserva)}")

    # Comprobar distribución de actividades
    print("\n=== ACTIVIDADES DESPUÉS DEL BALANCEO ===")

    df_comparacion = pd.concat([
        df_femenino,
        df_masculino_balanceado
    ])

    print(pd.crosstab(
        df_comparacion['Workout_Type'],
        df_comparacion['Gender']
    ))

    # Eliminar Gender de los datasets utilizados por la red
    df_femenino.drop(columns=['Gender'], inplace=True)

    df_masculino_balanceado.drop(
        columns=['Gender'], inplace=True
    )

    # Crear carpetas
    os.makedirs('datasets', exist_ok=True)
    os.makedirs('datasets/reserva', exist_ok=True)

    # Guardar datasets principales
    df_femenino.to_csv(
        'datasets/fitness_dataset1_femenino.csv',
        index=False
    )

    df_masculino_balanceado.to_csv(
        'datasets/fitness_dataset2_masculino.csv',
        index=False
    )

    # Guardar registros reservados
    # Conservamos Gender para identificar su procedencia
    df_masculino_reserva.to_csv(
        'datasets/reserva/fitness_masculino_reserva.csv',
        index=False
    )

    print("\n¡Proceso terminado con éxito!")
    print(f"Dataset femenino: {len(df_femenino)} registros.")
    print(f"Dataset masculino: {len(df_masculino_balanceado)} registros.")
    print(f"Registros masculinos de reserva: {len(df_masculino_reserva)}.")


if __name__ == "__main__":

    ruta_original = os.path.join(
        "datasets",
        "gym_members_exercise_tracking.csv"
    )

    preparar_datasets_por_genero(ruta_original)