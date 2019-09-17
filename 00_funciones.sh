#!/bin/bash

DIR_DATOS=Datos
DIR_UBICACIONES=Ubicaciones
DIR_MODELOS_LSTM=ModelosLSTM
DIR_GRAF_LSTM=GraficosLSTM
DIR_MODELOS_MLP=ModelosMLP
DIR_GRAF_MLP=GraficosMLP
DIR_MUESTRAS_LSTM=MuestrasLSTM
DIR_MUESTRAS_MLP=MuestrasMLP

espera_max_concurrentes () {
    local MAX=$1
    local TIEMPO=$2

    EJECUTANDO=`jobs -l | wc -l`
    while [ $EJECUTANDO -ge $MAX ]
    do
        echo `date +%H:%M:%S` Ejecutando: $EJECUTANDO
        jobs > /dev/null
        sleep $TIEMPO
        EJECUTANDO=`jobs -l | wc -l`
    done
}

