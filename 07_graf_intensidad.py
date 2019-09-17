#!/usr/bin/env python3
import sys
import glob
#from numpy import array
from pandas import read_csv
from pandas import merge
from pandas import concat
from pandas import to_datetime
from matplotlib import pyplot
import matplotlib.dates as mdates

dir_datos='./Datos/*/'
dir_salida='./salida'

if len(sys.argv) < 2:
    print ("Es necesario al menos un identificador de punto de medida.", file=sys.stderr)
    exit(1)

# carga precipitaciones
precipitaciones = read_csv('precipitaciones.csv', header=None, names=('Fecha','Precipitacion'))
precipitaciones['Fecha'] = to_datetime(precipitaciones['Fecha'], dayfirst=True)
precipitaciones.drop_duplicates(inplace=True)
precipitaciones.set_index('Fecha', inplace=True)
precipitaciones = precipitaciones.resample('15min').ffill()

# carga festivos
festivos = read_csv('festivos.csv', index_col=0, parse_dates=True, header=None, names=('Fecha','Festivo'))

for id in sys.argv[1:]:
    lista_csv = glob.glob(dir_datos + id + '.csv')
    if len(lista_csv) == 0:
        print ('Error: Pto. traf.:', id, 'No hay ficheros CSV de datos de tráfico')
        continue

    # carga trafico
    trafico = concat((read_csv(f, sep=';', index_col=1, parse_dates=True, header=None, names=('Id','Fecha','Intensidad','Ocupacion','Carga')) for f in lista_csv))
    #trafico = trafico.resample('15min').ffill()

    # nuevo dataframe con precipitaciones, trafico, hora y marca de fin de semana 
    dataset = merge(precipitaciones, trafico, on='Fecha')
    dataset = merge(dataset, festivos, on='Fecha')
    dataset = dataset[['Precipitacion','Festivo','Intensidad']]
    dataset.sort_index(inplace=True)

    fig, ax = pyplot.subplots(figsize=(15, 10))
    pyplot.ylabel('Pto: ' + id + '. Intensidad tráfico / Prep * 50 / Festivo')
    ax.plot(dataset['Intensidad'], label='Intensidad')
    ax.plot(dataset['Precipitacion']*50, label='Precipitacion')
    ax.plot(dataset['Festivo']*100, label='Festivo')
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M'))
    fig.autofmt_xdate(rotation=60)
    pyplot.savefig(dir_salida+'/'+id+'.png', bbox_inches='tight')
    #pyplot.show()
    pyplot.close()
    print (id)
