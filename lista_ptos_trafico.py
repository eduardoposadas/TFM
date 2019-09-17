#!/usr/bin/env python3
import sys
from lxml import etree

def kml_parser(fichEntrada):
    parser = etree.XMLParser(encoding="utf-8")
    tree = etree.parse(fichEntrada, parser)
    if len(parser.error_log) > 0:
        print ("Error analizando xml:" + fichEntrada, file=sys.stderr)
        for error in parser.error_log:
            print("linea" + error.line + ":" + error.column + " " + error.message, file=sys.stderr)
        exit()

    kml=tree.getroot()
    document=kml[0]
    folder=document[1]
    placemarkDict={}

    for placemark in folder:
        if not placemark.tag.endswith("Placemark"):
            continue

        temp={}
        for simpleData in placemark[1][0]:
            name=simpleData.get("name")
            if name == "IDELEM" or name == "idelem" or name == "id":
                i = int(simpleData.text)
            elif name == "COORD_X" or name == "x" or name == "utm_x":
                temp["utm_x"] = float(simpleData.text)
            elif name == "COORD_Y" or name == "y" or name == "utm_y":
                temp["utm_y"] = float(simpleData.text)
            else:
                temp[name] = simpleData.text

        placemarkDict[i] = temp
    
    return placemarkDict



if len(sys.argv) < 2:
    print ("Es necesario al menos el nombre de un fichero.", file=sys.stderr)
    exit()

lista_dict=[]
for f in sys.argv[1:]:
    lista_dict.append(kml_parser(f))

interseccion = lista_dict[0].keys()
for pd in lista_dict[1:]:
    interseccion = interseccion & pd.keys()

for i in interseccion:
    #print(i, "=> ", lista_dict[1][i])
    print(i, " ")
