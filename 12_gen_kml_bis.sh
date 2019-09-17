#!/bin/bash 
. 00_funciones.sh

for ZIP in 202468-38-intensidad-trafico.zip 202468-41-intensidad-trafico.zip 202468-44-intensidad-trafico.zip 202468-47-intensidad-trafico.zip
do
    mkdir -vp $DIR_UBICACIONES/$ZIP
    unzip -d $DIR_UBICACIONES/$ZIP $ZIP
    FICH=`basename $DIR_UBICACIONES/$ZIP/*.shp`
    FICH=${FICH%%.shp}
    ogr2ogr -f KML $DIR_UBICACIONES/$ZIP/$FICH.kml $DIR_UBICACIONES/$ZIP/$FICH.shp
done
