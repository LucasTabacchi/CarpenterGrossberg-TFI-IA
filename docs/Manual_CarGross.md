# Manual de referencia - CarGross.py

## Alcance

`CarGross.py` implementa una red Carpenter-Grossberg clasica y didactica. El objetivo es agrupar registros de clientes en clusters sin usar etiquetas previas.

El programa:

- lee archivos CSV;
- valida cantidad minima de filas;
- usa variables numericas indicadas por el usuario;
- binariza variables mediante umbrales;
- aplica el algoritmo Carpenter-Grossberg;
- genera un CSV con clusters y etiquetas interpretativas;
- genera un resumen de corrida con sensibilidad por `rho`;
- informa errores de uso con ayuda por consola.

## Limitaciones

- La version clasica usa patrones binarios 0/1.
- Las variables categoricas deben estar convertidas antes a numeros.
- El resultado depende del orden de las filas.
- El resultado depende del valor de vigilancia `rho`.
- Los nombres comerciales de perfiles son interpretaciones posteriores; la red solo devuelve clusters.

## Instalacion

Requisito: Python 3.10 o superior.

```powershell
cd C:\Users\lucas\Documents\Playground\CarpenterGrossberg_TFI
python --version
python -m pip install -r requirements.txt
```

Para usar el programa no se requieren librerias externas. `pytest` solo se usa para pruebas.

## Formato del CSV

El CSV debe tener encabezados. Para cumplir el TFI debe tener al menos 50 filas y 5 variables de entrada.

Ejemplo de columnas:

```text
id_cliente,frecuencia_compra,monto_total,monto_promedio,cantidad_productos,dias_desde_ultima_compra
```

Se recomienda indicar `--features` para controlar exactamente que variables entran a la red. Si no se indican, el programa infiere columnas numericas y omite identificadores como `id`, `id_cliente` o `cliente_id`.

## Uso

```powershell
python CarGross.py --input datasets\online_retail_procesado.csv --features frecuencia_compra,monto_total,monto_promedio,cantidad_productos,dias_desde_ultima_compra --id-column id_cliente --rho 0.8 --output outputs\resultados_online_retail.csv --summary outputs\resumen_online_retail.txt
```

## Parametros

- `--input`: CSV de entrada.
- `--features`: variables numericas separadas por coma.
- `--id-column`: columna identificadora opcional.
- `--rho`: parametro de vigilancia entre 0 y 1.
- `--thresholds`: CSV opcional con columnas `feature,threshold`.
- `--rho-sensitivity`: valores de rho separados por coma para agregar una mini sensibilidad al resumen. Por defecto, `0.6,0.8,0.95`. Use `""` para desactivar.
- `--output`: CSV de resultados.
- `--summary`: TXT de resumen.
- `--min-rows`: minimo de filas requeridas. Por defecto, 50.

## Salida esperada

El CSV de salida conserva las columnas originales y agrega:

- `cluster`: numero de cluster asignado.
- `perfil_estimado`: etiqueta interpretativa calculada desde los promedios originales del cluster y los umbrales de binarizacion.

El resumen incluye:

- cantidad de clientes procesados;
- variables usadas;
- valor de vigilancia;
- cantidad de clusters;
- distribucion por cluster;
- umbrales de binarizacion;
- prototipos binarios aprendidos;
- promedios por cluster e interpretacion;
- sensibilidad de cantidad de clusters ante distintos valores de `rho`.

## FAQ

**1. Por que hay que binarizar los datos?**

Porque la version clasica del algoritmo Carpenter-Grossberg del material trabaja con patrones binarios.

**2. Que pasa si cambio `rho`?**

Si sube `rho`, la red exige coincidencias mas fuertes y suele crear mas clusters. Si baja `rho`, agrupa patrones mas diferentes.

**3. El perfil estimado es una etiqueta real?**

No. Es una interpretacion posterior. La red devuelve clusters; luego el programa resume los promedios de las variables originales y arma una etiqueta como `alto_monto_bajo_recencia`.

## Referencias

- Richard P. Lippmann, "An Introduction to Computing with Neural Nets", IEEE ASSP Magazine, April 1987.
- `referencias/Lau.pp5.a.11.pdf`.
- `referencias/Lau.pp12.a.14.pdf`.
