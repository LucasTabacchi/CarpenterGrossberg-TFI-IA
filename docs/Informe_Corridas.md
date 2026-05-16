# Informe de corridas - CarGross.py

## Datos de la entrega

- Trabajo: Red Carpenter-Grossberg aplicada a segmentacion de clientes.
- Materia: Redes Neuronales.
- Archivo principal: `CarGross.py`.
- Valor de vigilancia usado: `rho = 0.8`.

## Dataset 1: online_retail_procesado.csv

Archivo: `datasets/online_retail_procesado.csv`

Cantidad de registros: 60 clientes.

Variables usadas:

- `frecuencia_compra`
- `monto_total`
- `monto_promedio`
- `cantidad_productos`
- `dias_desde_ultima_compra`

Comando:

```powershell
python CarGross.py --input datasets\online_retail_procesado.csv --features frecuencia_compra,monto_total,monto_promedio,cantidad_productos,dias_desde_ultima_compra --id-column id_cliente --rho 0.8 --output outputs\resultados_online_retail.csv --summary outputs\resumen_online_retail.txt
```

Resultado:

- Clientes procesados: 60.
- Clusters encontrados: 9.
- Archivo de resultados: `outputs/resultados_online_retail.csv`.
- Resumen: `outputs/resumen_online_retail.txt`.

Interpretacion:

El dataset combina clientes frecuentes, clientes de alto valor, clientes sensibles a descuentos, clientes ocasionales y clientes con riesgo de abandono. Con `rho = 0.8`, la red separo varios subgrupos porque la vigilancia exige alta similitud entre cada cliente y el prototipo del cluster.

## Dataset 2: customer_shopping_behavior_procesado.csv

Archivo: `datasets/customer_shopping_behavior_procesado.csv`

Cantidad de registros: 60 clientes.

Variables usadas:

- `edad`
- `monto_compra`
- `uso_descuentos`
- `frecuencia_compra`
- `categoria_producto_codificada`

Comando:

```powershell
python CarGross.py --input datasets\customer_shopping_behavior_procesado.csv --features edad,monto_compra,uso_descuentos,frecuencia_compra,categoria_producto_codificada --id-column id_cliente --rho 0.8 --output outputs\resultados_customer_behavior.csv --summary outputs\resumen_customer_behavior.txt
```

Resultado:

- Clientes procesados: 60.
- Clusters encontrados: 4.
- Archivo de resultados: `outputs/resultados_customer_behavior.csv`.
- Resumen: `outputs/resumen_customer_behavior.txt`.

Interpretacion:

El segundo dataset produjo menos clusters, lo que indica que los patrones binarios resultantes fueron mas compatibles entre si. Esto permite mostrar que el numero de clusters no esta prefijado, sino que depende de los datos, la binarizacion y el valor de vigilancia.

## Conclusion

La implementacion cumple el comportamiento central de Carpenter-Grossberg: recibe patrones, compara con prototipos existentes, aplica vigilancia y crea un nuevo cluster cuando ningun prototipo alcanza el umbral. La segmentacion obtenida debe interpretarse analizando los promedios y caracteristicas de cada cluster.
