#!/bin/bash
. 00_funciones.sh

mkdir $DIR_MUESTRAS_LSTM
./LSTM_multivariante_genera_json_datos_prediccion.py `./lista_ptos_trafico.py Ubicaciones/202468-*/*kml`

mkdir $DIR_MUESTRAS_MLP
./MLP_multivariante_genera_json_datos_prediccion.py `./lista_ptos_trafico.py Ubicaciones/202468-*/*kml`
