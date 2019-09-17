#!/bin/bash 
. 00_funciones.sh

for ZIP in 202468-[0-9]-intensidad-trafico.zip 202468-[0-9][0-9]-intensidad-trafico.zip
do
    mkdir -vp $DIR_UBICACIONES/$ZIP
    unzip -d $DIR_UBICACIONES/$ZIP $ZIP
    FICH=`basename $DIR_UBICACIONES/$ZIP/*.shp`
    FICH=${FICH%%.shp}
    ogr2ogr -f KML $DIR_UBICACIONES/$ZIP/$FICH.kml $DIR_UBICACIONES/$ZIP/$FICH.shp
done

for RAR in 202468-[0-9][0-9]-intensidad-trafico.rar # 202468-[0-9]-intensidad-trafico.rar
do
    DIR=${RAR%%.rar}.zip
    mkdir -vp $DIR_UBICACIONES/$DIR
    unrar $RAR $DIR_UBICACIONES/$DIR
    FICH=`basename $DIR_UBICACIONES/$DIR/*.shp`
    FICH=${FICH%%.shp}
    ogr2ogr -f KML $DIR_UBICACIONES/$DIR/$FICH.kml $DIR_UBICACIONES/$DIR/$FICH.shp
done
