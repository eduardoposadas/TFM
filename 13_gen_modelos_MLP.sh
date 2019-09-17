#!/bin/bash
. 00_funciones.sh

#Procesos simultaneos de generacion de modelos
MAX_CONCURRENTES=4
ESPERA=10

# Lista de todos los puntos de medicion de trafico que están en todos los ficheros KML
LISTA=`./lista_ptos_trafico.py $DIR_UBICACIONES/*/*.kml`
LISTA_RESTANTES=" $LISTA "

echo Generando modelos para los puntos de medicion:
echo $LISTA

mkdir $DIR_MODELOS_MLP $DIR_GRAF_MLP

# Configuracion para CUDA. Ejecutar en CPU, no en GPU
export CUDA_VISIBLE_DEVICES=""

for PTO in $LISTA
do
    ./MLP_multivariante.py ${PTO} $DIR_DATOS/*/${PTO}.csv >${PTO}_MLP_multivariante_salida.txt 2>&1 &

    #LISTA_RESTANTES=${LISTA_RESTANTES/$PTO/}
    #echo "Restantes: "` awk -F" " '{print NF}' <<< $LISTA_RESTANTES `
    LISTA_RESTANTES=`egrep -v "^$PTO  $"  <<< $LISTA_RESTANTES`
    echo "Ocurrencias: " $LISTA_RESTANTES
    echo "Restantes: "` wc -l <<< $LISTA_RESTANTES `
    
    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA

    mv -f *_MLP_multivariante_modelo.h5 $DIR_MODELOS_MLP
    mv -f *_MLP_multivariante_entrenamiento.png *_MLP_multivariante_prediccion.png $DIR_GRAF_MLP
done

espera_max_concurrentes 1 $ESPERA
mv -f *_MLP_multivariante_modelo.h5 $DIR_MODELOS_MLP
mv -f *_MLP_multivariante_entrenamiento.png *_MLP_multivariante_prediccion.png $DIR_GRAF_MLP
