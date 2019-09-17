#!/bin/bash
. 00_funciones.sh

MAX_CONCURRENTES=70
ESPERA=10

LISTA=`./lista_ptos_trafico.py $DIR_UBICACIONES/*/*.kml`
LISTA_RESTANTES=$LISTA

#. ~/Datos/LSTM/a/venv/bin/activate

for PTO in $LISTA
do
    mkdir $DIR_MODELOS_LSTM/$PTO
    tensorflowjs_converter --input_format keras $DIR_MODELOS_LSTM/${PTO}_LSTM_multivariante_modelo.h5 $DIR_MODELOS_LSTM/$PTO &

     mkdir $DIR_MODELOS_MLP/$PTO
     tensorflowjs_converter --input_format keras $DIR_MODELOS_MLP/${PTO}_MLP_multivariante_modelo.h5 $DIR_MODELOS_MLP/$PTO &
    
    #LISTA_RESTANTES=${LISTA_RESTANTES/$PTO/}
    #echo "Restantes: "` awk -F" " '{print NF}' <<< $LISTA_RESTANTES `
    LISTA_RESTANTES=`egrep -v "^$PTO  $"  <<< $LISTA_RESTANTES`
    echo "Restantes: "` wc -l <<< $LISTA_RESTANTES `
    
    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA
done

espera_max_concurrentes 1 $ESPERA

#deactivate
