import numpy as np
import os
import pandas as pd

from preprocesamiento import (
    cargar_datos,
    filtrar_por_edad,
    preprocesar_datos
)

from validaciones import (
    validar_dataset,
    validar_parametros,
    mostrar_man
)

# ============================================================
# FUNCIONES DE LA RED CARPENTER-GROSSBERG / FUZZY ART
# ============================================================

def fuzzy_and(vector_a, vector_b):
    """
    Operación AND difusa.

    En Fuzzy ART se utiliza el mínimo componente a componente.
    Ejemplo:
        A = [0.2, 0.8]
        B = [0.5, 0.4]

        resultado = [0.2, 0.4]
    """
    return np.minimum(vector_a, vector_b)


def norma_l1(vector):
    """
    Devuelve la suma de los componentes del vector.

    Esta medida se utiliza tanto para la función de elección
    como para la prueba de vigilancia.
    """
    return np.sum(vector)


def calcular_eleccion(usuario, cluster, alpha=0.001):
    """
    Calcula la función de elección de Fuzzy ART.

    Permite determinar qué cluster es inicialmente el mejor
    candidato para representar al usuario actual.

    Un valor mayor indica una mayor compatibilidad entre
    el usuario y el cluster.

    alpha evita divisiones problemáticas cuando el peso
    del cluster es muy pequeño.
    """
    interseccion = fuzzy_and(usuario, cluster)

    numerador = norma_l1(interseccion)
    denominador = alpha + norma_l1(cluster)

    return numerador / denominador


def calcular_match(usuario, cluster):
    """
    Calcula el grado de coincidencia entre el usuario
    y un cluster.

    El resultado se encuentra entre 0 y 1.

    Este valor se compara posteriormente con el parámetro
    de vigilancia.
    """
    interseccion = fuzzy_and(usuario, cluster)

    numerador = norma_l1(interseccion)
    denominador = norma_l1(usuario)

    # Protección ante un vector vacío o completamente nulo.
    if denominador == 0:
        return 0.0

    return numerador / denominador


def actualizar_cluster(cluster, usuario, beta=1.0):
    """
    Actualiza el prototipo del cluster utilizando la
    regla de aprendizaje de Fuzzy ART.

    beta representa la velocidad de aprendizaje.

    beta = 1.0:
        aprendizaje rápido; el cluster incorpora
        directamente la intersección entre el patrón
        nuevo y el conocimiento previo.

    Valores menores producen una actualización gradual.
    """
    interseccion = fuzzy_and(usuario, cluster)

    return (
        beta * interseccion
        + (1.0 - beta) * cluster
    )


def crear_cluster(usuario):
    """
    Crea una nueva categoría utilizando como prototipo
    inicial el patrón del usuario actual.
    """
    return usuario.copy()


def red_carpenter_grossberg(
    datos,
    vigilancia=0.70,
    alpha=0.001,
    beta=1.0
):
    """
    Implementa un agrupamiento adaptativo basado en
    Fuzzy ART de la familia Carpenter-Grossberg.

    Parámetros
    ----------
    datos:
        Matriz de usuarios previamente normalizados
        en el rango [0, 1].

    vigilancia:
        Valor entre 0 y 1 que determina qué grado de
        coincidencia debe alcanzar un usuario para
        incorporarse a un cluster existente.

    alpha:
        Parámetro utilizado por la función de elección.

    beta:
        Velocidad de aprendizaje de los clusters.

    Retorna
    -------
    clusters:
        Lista con los prototipos aprendidos.

    asignaciones:
        Cluster asignado a cada usuario.
    """

    clusters = []
    asignaciones = []

    for usuario in datos:

        # ----------------------------------------------------
        # Primer usuario:
        # al no existir categorías previas crea el primer cluster.
        # ----------------------------------------------------
        if len(clusters) == 0:
            clusters.append(crear_cluster(usuario))
            asignaciones.append(0)
            continue

        # ----------------------------------------------------
        # Calculamos la función de elección para TODOS
        # los clusters existentes.
        # ----------------------------------------------------
        elecciones = []

        for cluster in clusters:
            valor = calcular_eleccion(
                usuario,
                cluster,
                alpha
            )
            elecciones.append(valor)

        # Ordenamos los clusters desde el mejor candidato
        # hasta el de menor compatibilidad.
        candidatos = np.argsort(elecciones)[::-1]

        asignado = False

        # ----------------------------------------------------
        # Se evalúan los candidatos según su función de elección.
        # ----------------------------------------------------
        for indice_cluster in candidatos:

            cluster = clusters[indice_cluster]

            coincidencia = calcular_match(
                usuario,
                cluster
            )

            # ------------------------------------------------
            # PRUEBA DE VIGILANCIA
            # ------------------------------------------------
            if coincidencia >= vigilancia:

                clusters[indice_cluster] = actualizar_cluster(
                    cluster,
                    usuario,
                    beta
                )

                asignaciones.append(indice_cluster)
                asignado = True

                break

        # ----------------------------------------------------
        # Si ningún cluster supera la vigilancia,
        # se genera una nueva categoría.
        # ----------------------------------------------------
        if not asignado:

            clusters.append(
                crear_cluster(usuario)
            )

            asignaciones.append(
                len(clusters) - 1
            )

    return clusters, asignaciones

def generar_reporte_clusters(df_resultado, nombre_archivo_salida):
    """
    Genera un reporte descriptivo de los clusters obtenidos.

    IMPORTANTE:
    Esta función NO participa en el aprendizaje de la red.
    Analiza los resultados una vez terminada la corrida.

    Experience_Level se utiliza únicamente como referencia
    externa para estudiar la coherencia de los clusters.
    """

    reporte = []

    variables_promedio = [
        "BMI",
        "Resting_BPM",
        "Workout_Frequency",
        "Session_Duration",
        "Calories_Burned"
    ]

    # Recorremos cada cluster generado por la red
    for cluster_id in sorted(
        df_resultado["Cluster_Asignado"].unique()
    ):

        grupo = df_resultado[
            df_resultado["Cluster_Asignado"] == cluster_id
        ]

        cantidad = len(grupo)

        # ----------------------------------------------------
        # WORKOUT TYPE
        # ----------------------------------------------------

        conteo_workout = grupo["Workout_Type"].value_counts()

        workout_predominante = conteo_workout.index[0]
        cantidad_workout = conteo_workout.iloc[0]

        porcentaje_workout = (
            cantidad_workout / cantidad
        ) * 100

        distribucion_workout = "; ".join(
            f"{tipo}: {cant}"
            for tipo, cant in conteo_workout.items()
        )

        # ----------------------------------------------------
        # EXPERIENCE LEVEL
        # ----------------------------------------------------

        conteo_experiencia = (
            grupo["Experience_Level"].value_counts()
        )

        experiencia_predominante = conteo_experiencia.index[0]
        cantidad_experiencia = conteo_experiencia.iloc[0]

        porcentaje_experiencia = (
            cantidad_experiencia / cantidad
        ) * 100

        distribucion_experiencia = "; ".join(
            f"{nivel}: {cant}"
            for nivel, cant in conteo_experiencia.items()
        )

        # ----------------------------------------------------
        # FILA DEL REPORTE
        # ----------------------------------------------------

        fila = {
            "Cluster": cluster_id,
            "Cantidad_Usuarios": cantidad,

            "Workout_Predominante":
                workout_predominante,

            "Workout_Predominante_Porcentaje":
                round(porcentaje_workout, 2),

            "Distribucion_Workout":
                distribucion_workout,

            "Experience_Level_Predominante":
                experiencia_predominante,

            "Experience_Level_Porcentaje":
                round(porcentaje_experiencia, 2),

            "Distribucion_Experience_Level":
                distribucion_experiencia,
        }

        # ----------------------------------------------------
        # PROMEDIOS DE VARIABLES NUMÉRICAS
        # ----------------------------------------------------

        for variable in variables_promedio:

            if variable in grupo.columns:

                fila[f"Promedio_{variable}"] = round(
                    grupo[variable].mean(),
                    2
                )

        reporte.append(fila)

    # Convertimos el reporte a DataFrame
    df_reporte = pd.DataFrame(reporte)

    # Guardamos el archivo
    df_reporte.to_csv(
        nombre_archivo_salida,
        index=False
    )

    return df_reporte


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    # Directorio donde se encuentra CarGross.py
    carpeta_actual = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Cada dataset tiene su propio archivo de resultados.
    datasets = [
        (
            "fitness_dataset1_femenino.csv",
            "resultados_dataset1.csv"
        ),
        (
            "fitness_dataset2_masculino.csv",
            "resultados_dataset2.csv"
        ),
    ]

    # --------------------------------------------------------
    # Parámetros iniciales
    # --------------------------------------------------------

    # Vigilancia:
    # controla cuánto debe coincidir un usuario con un
    # cluster para poder incorporarse.
    vigilancia = 0.7

    # Alpha:
    # evita problemas de división y participa en la
    # función de elección.
    alpha = 0.001

    # Beta:
    # controla la velocidad de aprendizaje.
    beta = 1.0

    try:
        validar_parametros(
            vigilancia,
            alpha,
            beta
        )

    except ValueError as error:

        print("\nERROR DE CONFIGURACION:")
        print(error)

        mostrar_man()

        raise SystemExit(1)

    # --------------------------------------------------------
    # Procesamiento independiente de cada dataset
    # --------------------------------------------------------

    for nombre_entrada, nombre_salida in datasets:

        archivo_entrada = os.path.join(
            carpeta_actual,
            "datasets",
            nombre_entrada
        )

        print("\n--------------------------------------------")
        print(f"Buscando archivo: {archivo_entrada}")
        print("--------------------------------------------")

        try:

            # ----------------------------------------------------
             # 1. CARGA DEL CSV
            # ----------------------------------------------------

            df_original = cargar_datos(
                archivo_entrada
            )

            # ----------------------------------------------------
            # 2. VALIDACION
            # ----------------------------------------------------

            validar_dataset(
                df_original
            )

            # ----------------------------------------------------
            # 3. FILTRO DEL ALCANCE 20-40 ANOS
            # ----------------------------------------------------

            df_original = filtrar_por_edad(
                df_original
            )

            print(
                f"Procesando {len(df_original)} registros..."
            )

            # ----------------------------------------------------
            # 4. PREPROCESAMIENTO
            # ----------------------------------------------------

            datos_red, columnas, niveles_experiencia = (
                preprocesar_datos(
                    df_original
                )
            )

            # ----------------------------------------------------
            # 5. RED CARPENTER-GROSSBERG / FUZZY ART
            # ----------------------------------------------------

            clusters_finales, etiquetas = (
                red_carpenter_grossberg(
                    datos_red,
                    vigilancia=vigilancia,
                    alpha=alpha,
                    beta=beta
                )
            )

            # ------------------------------------------------
            # 6. GUARDAR RESULTADOS
            # ------------------------------------------------

            df_resultado = df_original.copy()

            df_resultado[
                "Cluster_Asignado"
            ] = etiquetas

            carpeta_salida = os.path.join(
                carpeta_actual,
                "output"
            )

            os.makedirs(
                carpeta_salida,
                exist_ok=True
            )

            ruta_salida = os.path.join(
                carpeta_salida,
                nombre_salida
            )

            df_resultado.to_csv(
                ruta_salida,
                index=False
            )

            # ------------------------------------------------
            # GENERAR REPORTE DESCRIPTIVO DE CLUSTERS
            # ------------------------------------------------

            nombre_reporte = (
                "reporte_" + nombre_salida
            )

            ruta_reporte = os.path.join(
                carpeta_salida,
                nombre_reporte
            )

            df_reporte = generar_reporte_clusters(
                df_resultado,
                ruta_reporte
            )

            print(
                f"Reporte de clusters guardado en: "
                f"{ruta_reporte}"
            )

            # ------------------------------------------------
            # 7. RESUMEN DE LA CORRIDA
            # ------------------------------------------------

            print("\nProceso finalizado correctamente.")

            print(
                f"Registros procesados: "
                f"{len(df_resultado)}"
            )

            print(
                f"Clusters generados: "
                f"{len(clusters_finales)}"
            )

            print(
                f"Vigilancia utilizada: "
                f"{vigilancia}"
            )

            print(
                f"Resultados guardados en: "
                f"{ruta_salida}"
            )

            # Cantidad de usuarios en cada cluster
            conteo_clusters = (
                pd.Series(etiquetas)
                .value_counts()
                .sort_index()
            )

            print("\nUsuarios por cluster:")

            for cluster_id, cantidad in conteo_clusters.items():

                print(
                    f"  Cluster {cluster_id}: "
                    f"{cantidad} usuarios"
                )

        except FileNotFoundError as error:

            print("\nERROR DE ARCHIVO:")
            print(error)

            mostrar_man()


        except PermissionError:

            print(
                "\nERROR DE PERMISOS:\n"
                "No fue posible acceder o escribir uno "
                "de los archivos."
            )

            mostrar_man()


        except ValueError as error:

            print("\nERROR EN LOS DATOS:")
            print(error)

            mostrar_man()


        except KeyError as error:

            print("\nERROR DE ESTRUCTURA DEL DATASET:")
            print(
                f"No se pudo encontrar la columna: {error}"
            )

            mostrar_man()


        except Exception as error:

            print("\nERROR INESPERADO:")
            print(error)

            mostrar_man()