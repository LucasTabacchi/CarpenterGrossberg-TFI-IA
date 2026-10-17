"""Experimentos reproducibles de vigilancia con los datasets definitivos."""
from pathlib import Path
import pandas as pd
from CarGross import red_carpenter_grossberg, generar_reporte_clusters
from preprocesamiento import cargar_datos, filtrar_por_edad, preprocesar_datos
from validaciones import validar_dataset, validar_parametros

BASE = Path(__file__).resolve().parent
VIGILANCIAS = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
ALPHA, BETA = 0.001, 1.0
DATASETS = {
    'femenino': 'fitness_dataset1_femenino.csv',
    'masculino': 'fitness_dataset2_masculino.csv',
}


def main():
    salida = BASE / 'output' / 'pruebas_vigilancia'
    salida.mkdir(parents=True, exist_ok=True)
    resumen = []

    for genero, archivo in DATASETS.items():
        ruta = BASE / 'datasets' / archivo
        df = cargar_datos(str(ruta))
        validar_dataset(df)
        df = filtrar_por_edad(df)
        datos, _, _ = preprocesar_datos(df)

        for rho in VIGILANCIAS:
            validar_parametros(rho, ALPHA, BETA)
            clusters, asignaciones = red_carpenter_grossberg(
                datos, vigilancia=rho, alpha=ALPHA, beta=BETA
            )
            resultado = df.copy()
            resultado['Cluster_Asignado'] = asignaciones
            carpeta = salida / f'rho_{round(rho * 100):03d}'
            carpeta.mkdir(parents=True, exist_ok=True)
            resultado.to_csv(carpeta / f'resultados_{genero}.csv', index=False)
            reporte = generar_reporte_clusters(
                resultado, str(carpeta / f'reporte_{genero}.csv')
            )
            tamanos = resultado['Cluster_Asignado'].value_counts()
            coherencia_workout = 100 * sum(
                g['Workout_Type'].value_counts().max()
                for _, g in resultado.groupby('Cluster_Asignado')
            ) / len(resultado)
            coherencia_experiencia = 100 * sum(
                g['Experience_Level'].value_counts().max()
                for _, g in resultado.groupby('Cluster_Asignado')
            ) / len(resultado)
            resumen.append({
                'Genero': genero,
                'Vigilancia': rho,
                'Registros': len(resultado),
                'Clusters': len(clusters),
                'Clusters_homogeneos_Workout': int((reporte['Workout_Predominante_Porcentaje'] == 100).sum()),
                'Clusters_3_o_menos': int((tamanos <= 3).sum()),
                'Clusters_1_usuario': int((tamanos == 1).sum()),
                'Mayor_cluster': int(tamanos.max()),
                'Coherencia_Workout_pct': round(coherencia_workout, 2),
                'Predominancia_Experience_pct': round(coherencia_experiencia, 2),
            })
            print(f'{genero:10} rho={rho:.2f}: {len(resultado)} registros, '
                  f'{len(clusters)} clusters, coherencia Workout={coherencia_workout:.2f}%')

    pd.DataFrame(resumen).to_csv(salida / 'resumen_vigilancias.csv', index=False)
    print(f'\nResumen guardado en: {salida / "resumen_vigilancias.csv"}')


if __name__ == '__main__':
    main()
