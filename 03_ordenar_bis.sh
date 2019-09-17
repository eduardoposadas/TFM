#!/bin/bash
. 00_funciones.sh

MAX_CONCURRENTES=$(( `grep -c processor /proc/cpuinfo` * 3 ))
ESPERA=0.2

for FILE in $DIR_DATOS/208627-71-transporte-ptomedida-historico.zip/*.csv $DIR_DATOS/208627-72-transporte-ptomedida-historico.zip/*.csv $DIR_DATOS/208627-73-transporte-ptomedida-historico.zip/*.csv $DIR_DATOS/208627-74-transporte-ptomedida-historico.zip/*.csv
do
    echo Ordenando: "$FILE"
    sort -o "${FILE}" "${FILE}" & 
    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA
done
