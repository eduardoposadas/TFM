#!/bin/bash
. 00_funciones.sh


MAX_CONCURRENTES=100
ESPERA=0.5

igualar_campos_1 () {
    echo Normalizando campos: "$1"
    [ ! -f "$1".temp ] && mv "$1" "$1".temp
    #awk -F\; '$3!="\"NaN\"" && $4!="\"NaN\"" && $5!="\"NaN\"" && $8 == "\"N\"" {print $1";"$2";"$3";"$4";"$5}' "$1".temp > "$1"
    awk -F\; 'NF==9  && $3!="\"NaN\"" && $4!="\"NaN\"" && $5!="\"NaN\"" && $8 == "\"N\""  {print $1";"$2";"$3";"$4";"$5}  \
              NF==11 && $6!="\"NaN\"" && $7!="\"NaN\"" && $8!="\"NaN\"" && $10 == "\"N\"" {print $1";"$2";"$6";"$7";"$8}' \
              "$1".temp > "$1"
}

igualar_campos_2 () {
    echo Normalizando campos: "$1"
    [ ! -f "$1".temp ] && mv "$1" "$1".temp
    awk -F\; '$6!="\"NaN\"" && $7!="\"NaN\"" && $8!="\"NaN\"" && $10 == "\"N\"" {print $1";"$2";"$6";"$7";"$8}' "$1".temp > "$1"
}

igualar_campos_3 () {
    echo Normalizando campos: "$1"
    [ ! -f "$1".temp ] && mv "$1" "$1".temp
    awk -F\; '$5!="\"NaN\"" && $6!="\"NaN\"" && $7!="\"NaN\"" && $9 == "\"N\"" {print $1";"$2";"$5";"$6";"$7}' "$1".temp > "$1"
}

igualar_campos_4 () {
    echo Normalizando campos: "$1"
    [ ! -f "$1".temp ] && mv "$1" "$1".temp
    awk -F\; '$5!="NaN" && $6!="NaN" && $7!="NaN" && $9 == "N" {print $1";"$2";"$5";"$6";"$7}' "$1".temp > "$1"
}

igualar_campos_5 () {
    echo Normalizando campos: "$1"
    [ ! -f "$1".temp ] && mv "$1" "$1".temp
    awk -F\; '$4!="\"NaN\"" && $5!="\"NaN\"" && $6!="\"NaN\"" && $8 == "\"N\"" {print $1";"$2";"$4";"$5";"$6}' "$1".temp > "$1"
}


for FILE in $DIR_DATOS/208627-{71..74}-transporte-ptomedida-historico.zip/*.csv
do
    igualar_campos_5 "${FILE}" &
    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA
done
