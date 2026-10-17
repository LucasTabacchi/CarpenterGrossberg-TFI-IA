import pandas as pd

# Cargar dataset original
df = pd.read_csv("datasets/gym_members_exercise_tracking.csv")

print("\n=== DISTRIBUCIÓN ORIGINAL POR GÉNERO ===")
print(df["Gender"].value_counts())

print("\n=== ACTIVIDADES POR GÉNERO ===")
print(pd.crosstab(df["Workout_Type"], df["Gender"]))

# Aplicar el filtro de edad de nuestro proyecto
df_filtrado = df[
    (df["Age"] >= 20) & (df["Age"] <= 40)
]

print("\n=== DISTRIBUCIÓN DESPUÉS DEL FILTRO DE EDAD ===")
print(df_filtrado["Gender"].value_counts())

print("\n=== ACTIVIDADES POR GÉNERO DESPUÉS DEL FILTRO ===")
print(pd.crosstab(
    df_filtrado["Workout_Type"],
    df_filtrado["Gender"]
))

print("\n=== DATASETS BALANCEADOS: FILTRO 20-40 AÑOS ===")

df_mujeres = pd.read_csv(
    "datasets/fitness_dataset1_femenino.csv"
)

df_hombres = pd.read_csv(
    "datasets/fitness_dataset2_masculino.csv"
)

df_mujeres = df_mujeres[
    df_mujeres["Age"].between(20, 40)
]

df_hombres = df_hombres[
    df_hombres["Age"].between(20, 40)
]

print(f"Mujeres de 20 a 40 años: {len(df_mujeres)}")
print(f"Hombres de 20 a 40 años: {len(df_hombres)}")

print("\n=== ACTIVIDADES DESPUÉS DEL FILTRO ===")

distribucion = pd.DataFrame({
    "Mujeres": df_mujeres["Workout_Type"].value_counts(),
    "Hombres": df_hombres["Workout_Type"].value_counts()
}).fillna(0).astype(int)

print(distribucion)