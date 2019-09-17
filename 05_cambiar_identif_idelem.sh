#!/bin/bash
. 00_funciones.sh


# Correspondencia entre identif y idelem

for file in $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/*.csv
do
    # El campo identif es el nombre del fichero sin extension csv
    identif=${file#$DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/}
    identif=${identif%.csv}
    
    # El campo idelem es el nombre del fichero del año 2015 en el que se encuentra $identif sin extension csv
    idelem=`fgrep -l ";\"$identif\";" $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/*.csv`
    idelem=${idelem#$DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/}
    idelem=${idelem%.csv}
    
    echo $identif $idelem
done > $DIR_DATOS/salida


#Correcciones manuales
awk '$1 == "11010" {print "11010 3615"; next} \
     $1 == "13018" {print "13018 4166"; next} \
     $1 == "31051" {print "31051 3735"; next} \
     $1 == "43004" {print "43004 5417"; next} \
     $1 == "62077" {print "62077 5687"; next} \
     $1 == "75022" {print "75022 6954"; next} \
     $1 == "75023" {print "75023 7110"; next} \
     $1 == "77402" {print "77402 6585"; next} \
     $1 == "51014" {print "51014 5127"; next} \
     $1 == "51029" {print "51029 5111"; next} \
                   {print}' $DIR_DATOS/salida > $DIR_DATOS/salida_corregida

MAX_CONCURRENTES=50
ESPERA=0.5

cat $DIR_DATOS/salida_corregida | while read identif idelem
do
    if [ ! -z "$idelem" ]
    then
        if [ -f $DIR_DATOS/208627-19-transporte-ptomedida-historico.zip/$identif.csv ]
        then
            echo Corrigiendo Id en $DIR_DATOS/208627-19-transporte-ptomedida-historico.zip/"$identif".csv
            sed -i "s/^$identif\;/$idelem\;/" $DIR_DATOS/208627-19-transporte-ptomedida-historico.zip/"$identif".csv &
        fi
        if [ -f $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/$identif.csv ]
        then
            echo Corrigiendo Id en $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/"$identif".csv
            sed -i "s/^$identif\;/$idelem\;/" $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/"$identif".csv &
        fi
    fi
    espera_max_concurrentes $MAX_CONCURRENTES $ESPERA
done

espera_max_concurrentes 1 $ESPERA

cat $DIR_DATOS/salida_corregida | while read identif idelem
do
    if [ ! -z "$idelem" ]
    then
        if [ -f $DIR_DATOS/208627-19-transporte-ptomedida-historico.zip/$identif.csv ]
        then
            mv -v $DIR_DATOS/208627-19-transporte-ptomedida-historico.zip/"$identif".csv $DIR_DATOS/208627-19-transporte-ptomedida-historico.zip/"$idelem".csv
        fi
        if [ -f $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/"$identif".csv ]
        then
            mv -v $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/"$identif".csv $DIR_DATOS/208627-20-transporte-ptomedida-historico.zip/"$idelem".csv 
        fi
    fi
done


# Correcciones manuales
mv $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5111.csv $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5111.csv.temp
mv $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5127.csv $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5127.csv.temp
sed 's/^5111/5127/' $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5111.csv.temp > $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5127.csv
sed 's/^5127/5111/' $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5127.csv.temp > $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5111.csv
rm $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5111.csv.temp $DIR_DATOS/208627-18-transporte-ptomedida-historico.zip/5127.csv.temp

mv $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5127.csv $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5127.csv.temp
mv $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5111.csv $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5111.csv.temp
fgrep -h ";\"51029\";" $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5127.csv.temp \
                       $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5111.csv.temp \
      | sed 's/^5127/5111/' > $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5111.csv
fgrep -h ";\"51014\";" $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5111.csv.temp \
                       $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5127.csv.temp \
      | sed 's/^5111/5127/' > $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5127.csv
rm $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5127.csv.temp $DIR_DATOS/208627-21-transporte-ptomedida-historico.zip/5111.csv.temp



#Comprobar si un pto con coordenadas tiene datos
#for pto in `gawk 'match($0, "<SimpleData name=.id.>([0-9]+)</SimpleData>", m) {print m[1]}' ubicacion/20170123_pmed_ubicacion/Pto_medida_03_2019.kml`; do if [ -f Datos/208627-70-transporte-ptomedida-historico.zip/${pto}.csv ]; then echo "${pto}.csv"; else echo -e "${pto}.csv \tNo"; fi ; done 
