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

    # Renombramos las columnas de Kaggle a los nombres limpios de tu diseño
    df.rename(columns={
        'Workout_Frequency (days/week)': 'Workout_Frequency',
        'Session_Duration (hours)': 'Session_Duration'
    }, inplace=True)

    # Variables seleccionadas en el diseño técnico + Gender (para dividir)
    columnas_utiles = [
        'Age', 'BMI', 'Resting_BPM', 'Workout_Type', 
        'Workout_Frequency', 'Session_Duration', 'Calories_Burned', 
        'Experience_Level', 'Gender'
    ]
    
    # Seleccionamos las columnas y conservamos la limpieza de filas vacías.
    # Aquí no filtramos edades: esa regla se aplica en preprocesamiento.py
    # al cargar cualquier CSV desde CarGross.py, antes de enviarlo a la red.
    df_filtrado = df[columnas_utiles].dropna().copy()

    # Dividir por género
    df_femenino = df_filtrado[df_filtrado['Gender'] == 'Female'].copy()
    df_masculino = df_filtrado[df_filtrado['Gender'] == 'Male'].copy()

    # Eliminar la columna 'Gender' ya que no se usará en la red
    df_femenino.drop(columns=['Gender'], inplace=True)
    df_masculino.drop(columns=['Gender'], inplace=True)

    # Crear la carpeta y guardar los archivos
    os.makedirs('datasets', exist_ok=True)
    df_femenino.to_csv('datasets/fitness_dataset1_femenino.csv', index=False)
    df_masculino.to_csv('datasets/fitness_dataset2_masculino.csv', index=False)
    
    print("\n¡Proceso terminado con éxito!")
    print(f"Dataset 1 (Femenino) guardado en carpeta 'datasets' con {len(df_femenino)} registros.")
    print(f"Dataset 2 (Masculino) guardado en carpeta 'datasets' con {len(df_masculino)} registros.")

if __name__ == "__main__":
    
    ruta_original = os.path.join("datasets", "gym_members_exercise_tracking.csv")
    preparar_datasets_por_genero(ruta_original)
