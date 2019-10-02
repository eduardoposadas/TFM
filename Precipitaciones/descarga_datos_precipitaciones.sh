#!/bin/bash 

DIA_INI=13
MES_INI=07
ANO_INI=2017

DIA_FIN=1
MES_FIN=10
ANO_FIN=2019

FICH_SALIDA=precipitaciones.csv

#Convierte la pagina html de oginet en un CSV con el formato fecha, precipitacion
crea_csv (){
awk '
/onmouseover=.return overlib.*[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]/{
    split($0, a, ">")
    fecha=substr(a[3], 0, index(a[3], "<") -1 )
}

/onmouseover=.return overlib.*[0-9][0-9]:[0-9][0-9]/{
    split($0, a, ">")
    hora=substr(a[3], 0, index(a[3], "<") -1 )
}

/TD align="center" bgcolor=".*h<\/font>/{
    split($0, a, ">")
    precipitacion=substr(a[3], 0, index(a[3], "<") -1 )
    if ( substr(precipitacion, index(precipitacion, "/")) != "/1h"){
        precipitacion="0.0"
    } else {
        precipitacion=substr(precipitacion, 0, index(precipitacion, "/") -1 )
    }
    print fecha" "hora","precipitacion
}
'
}


ESTACION=08222 #MADRID-RETIRO
DIA_GET=$DIA_INI
MES_GET=$MES_INI
ANO_GET=$ANO_INI
FECHA_GET=`date -d $ANO_GET-$MES_GET-$DIA_GET +%s`
FECHA_FIN=`date -d $ANO_FIN-$MES_FIN-$DIA_FIN +%s`

while [ $FECHA_FIN -gt $FECHA_GET ]
do
    FICH=$ESTACION-$ANO_GET-$MES_GET-$DIA_GET.html
    curl "https://www.ogimet.com/cgi-bin/gsynres?ind=$ESTACION&decoded=yes&ndays=1&ano=$ANO_GET&mes=$MES_GET&day=$DIA_GET&hora=0" > $FICH

    # Suma un dia
    DIA=`date -d "$ANO_GET-$MES_GET-$DIA_GET tomorrow" +%d`
    MES=`date -d "$ANO_GET-$MES_GET-$DIA_GET tomorrow" +%m`
    ANO=`date -d "$ANO_GET-$MES_GET-$DIA_GET tomorrow" +%Y`
    DIA_GET=`date -d "$ANO-$MES-$DIA" +%d`
    MES_GET=`date -d "$ANO-$MES-$DIA" +%m`
    ANO_GET=`date -d "$ANO-$MES-$DIA" +%Y`
    FECHA_GET=`date -d $ANO_GET-$MES_GET-$DIA_GET +%s`
done

cat *.html | crea_csv > $FICH_SALIDA
