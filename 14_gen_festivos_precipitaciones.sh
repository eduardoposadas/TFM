#!/bin/bash
. 00_funciones.sh

echo Genera fichero CSV con festivos en Madrid
./Calendario_laboral.py

echo Genera fichero CSV con las precipitaciones registradas en Madrid-Retiro
cd Precipitaciones
./descarga_datos_precipitaciones.sh
cp precipitaciones.csv ..
cd ..

