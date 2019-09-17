#!/bin/bash 
. 00_funciones.sh

ulimit -n 20000
trap "jobs >/dev/null" SIGCHLD

MAX_CONCURRENTES=$(( `grep -c processor /proc/cpuinfo` * 2 ))
ESPERA=60

for ZIP in 208627-[0-9]-transporte-ptomedida-historico.zip 208627-[0-9][0-9]-transporte-ptomedida-historico.zip
do
    if [ "$ZIP" == 208627-46-transporte-ptomedida-historico.zip ]
    then
        SEP=,
    else
        SEP=\;
    fi
    mkdir -vp $DIR_DATOS/$ZIP
    unzip -p $ZIP |( cd $DIR_DATOS/$ZIP; awk -F$SEP 'BEGIN{OFS=";"} {f=$1;gsub(/\"/,"", f); $1=f; print >> f".csv" }' ) &

    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA
done

espera_max_concurrentes 1 $ESPERA
