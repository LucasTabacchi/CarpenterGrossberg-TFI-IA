# Guion de audio - Presentacion CarGross

## Diapositiva 1

En esta presentación expongo el Trabajo Final Integrador sobre la red Carpenter-Grossberg aplicada a la segmentación de clientes. El enfoque elegido combina teoría de redes neuronales, una implementación clásica en Python y resultados obtenidos con dos datasets de prueba.

## Diapositiva 2

El trabajo práctico no pide solamente una explicación teórica. También exige una implementación funcional, documentación, datasets de uso e informe de corridas. Por eso la propuesta se pensó como una entrega completa que une teoría, código y evidencia experimental.

## Diapositiva 3

La red Carpenter-Grossberg surge dentro del marco de Adaptive Resonance Theory. Su valor principal es que permite aprender nuevas categorías sin destruir las ya aprendidas. Esa combinación entre plasticidad y estabilidad es una de las ideas más importantes detrás de ART.

## Diapositiva 4

El funcionamiento general de la red es secuencial. Cada patrón de entrada se compara con prototipos existentes, se selecciona el mejor candidato y luego se aplica el test de vigilancia. Si el parecido alcanza el umbral, el prototipo se adapta; si no, se crea una categoría nueva.

## Diapositiva 5

El parámetro de vigilancia, rho, controla qué tan estricta es la comparación. Si rho es bajo, la red agrupa más. Si rho es alto, exige coincidencias más fuertes y genera más clusters. En este trabajo se usó rho igual a 0.80 para mostrar bien la aparición de subgrupos.

## Diapositiva 6

La aplicación elegida fue la segmentación de clientes según comportamiento de compra. Esta elección es adecuada porque no siempre se conoce de antemano cuántos perfiles comerciales existen. Por eso una red no supervisada e incremental resulta una alternativa muy clara para este caso.

## Diapositiva 7

La implementación se realizó en el archivo CarGross.py. El programa lee archivos CSV, valida los datos, selecciona variables numéricas, binariza los valores mediante umbrales y luego aplica la red Carpenter-Grossberg clásica. Finalmente, genera un archivo de resultados y un resumen de corrida.

## Diapositiva 8

En el primer dataset, Online Retail procesado, la red encontró 9 clusters. Este resultado muestra que con una vigilancia relativamente alta el modelo separa varios subperfiles dentro de un mismo universo de clientes. Eso vuelve más rica la interpretación de la segmentación.

## Diapositiva 9

En el segundo dataset, Customer Shopping Behavior, la red encontró 4 clusters. Esto demuestra que la cantidad de categorías no está fijada por anticipado, sino que depende de la estructura de los datos y de cómo esos datos quedan representados en forma binaria.

## Diapositiva 10

Si comparamos Carpenter-Grossberg con otras redes, vemos diferencias claras. El perceptrón es supervisado, Hopfield funciona como memoria asociativa, Hamming elige el patrón más parecido entre ejemplares ya definidos y K-means requiere fijar previamente la cantidad de clusters. Carpenter-Grossberg, en cambio, puede crear nuevas categorías durante el aprendizaje.

## Diapositiva 11

Entre las fortalezas de esta red se destacan el aprendizaje no supervisado, la creación dinámica de categorías y su gran valor didáctico. Entre sus debilidades aparecen la dependencia del parámetro rho, la sensibilidad al orden de entrada y la necesidad de preprocesamiento, especialmente porque la versión clásica trabaja mejor con datos binarios.

## Diapositiva 12

Como conclusión, Carpenter-Grossberg fue una buena elección para este trabajo porque permitió mostrar de manera clara la lógica del aprendizaje no supervisado y además implementarla en Python con resultados concretos. La red no etiqueta clientes por sí sola: descubre clusters, y luego esos clusters se interpretan en términos de negocio.
