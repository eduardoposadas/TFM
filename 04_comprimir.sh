#!/bin/bash
. 00_funciones.sh

MAX_CONCURRENTES=`grep -c processor /proc/cpuinfo`
ESPERA=10

for DIR in $DIR_DATOS/*
do
    if [ -d $DIR ]
    then
        echo Comprimiendo: $DIR
        ( cd $DIR; xz * ) &
    fi

    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA
done
