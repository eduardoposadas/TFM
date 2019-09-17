#!/bin/bash
. 00_funciones.sh

# echo Genera fichero CSV con festivos en Madrid
# ./Calendario_laboral.py
# 
# echo Genera fichero CSV con las precipitaciones registradas en Madrid-Retiro
# cd Precipitaciones
# ./descarga_datos_precipitaciones.sh
# cp precipitaciones.csv ..
# cd ..

#Procesos simultaneos de generacion de modelos
MAX_CONCURRENTES=4
ESPERA=5

# Lista de todos los puntos de medicion de trafico que están en todos los ficheros KML
LISTA=`./lista_ptos_trafico.py $DIR_UBICACIONES/*/*.kml`
LISTA_RESTANTES=" $LISTA "

echo Generando modelos para los puntos de medicion:
echo $LISTA

mkdir $DIR_MODELOS_LSTM $DIR_GRAF_LSTM

# # Configuracion para Tensorflow. No reserva toda la memoria de la GPU y asi se pueden lanzar varios procesos Tensorflow.
# export TF_FORCE_GPU_ALLOW_GROWTH=true

# Configuracion para CUDA. Ejecutar en CPU, no en GPU
export CUDA_VISIBLE_DEVICES=""


for PTO in $LISTA
do
    ./LSTM_multivariante.py ${PTO} $DIR_DATOS/*/${PTO}.csv >${PTO}_LSTM_multivariante_salida.txt 2>&1 &

    #LISTA_RESTANTES=${LISTA_RESTANTES/$PTO/}
    #echo "Restantes: "` awk -F" " '{print NF}' <<< $LISTA_RESTANTES `
    LISTA_RESTANTES=`egrep -v "^$PTO  $"  <<< $LISTA_RESTANTES`
    echo "Restantes: "` wc -l <<< $LISTA_RESTANTES `
    
    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA

    mv -f *_LSTM_multivariante_modelo.h5 $DIR_MODELOS_LSTM
    mv -f *_LSTM_multivariante_entrenamiento.png *_LSTM_multivariante_prediccion.png $DIR_GRAF_LSTM
done

espera_max_concurrentes 1 $ESPERA
mv -f *_LSTM_multivariante_modelo.h5 $DIR_MODELOS_LSTM
mv -f *_LSTM_multivariante_entrenamiento.png *_LSTM_multivariante_prediccion.png $DIR_GRAF_LSTM
