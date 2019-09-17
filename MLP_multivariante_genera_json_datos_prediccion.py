#!/usr/bin/env python3
import sys
import glob
import json
from numpy import array
from pandas import read_csv
from pandas import merge
from pandas import concat
from pandas import to_datetime
from sklearn.preprocessing import MinMaxScaler

dir_salida = './MuestrasMLP'
dir_datos='./Datos/*/'

# formatea para modelo
def formateaMuestras(muestras, n_steps_in, n_steps_out):
	X, y = list(), list()
	for i in range(len(muestras)):
		# find the end of this pattern
		end_ix = i + n_steps_in
		out_end_ix = end_ix + n_steps_out-1
		# check if we are beyond the dataset
		if out_end_ix > len(muestras):
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = muestras[i:end_ix, :-1], muestras[end_ix-1:out_end_ix, -1]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)


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

# Carga fechas de inicio y fin de las muestras
with open('configuracion.json') as fichFechas:
    conf = json.load(fichFechas)

for id in sys.argv[1:]:
    lista_csv = glob.glob(dir_datos + id + '.csv')
    print('Generando fichero JSON con muestras para predicción web MLP para pto. medida:', id)
    
    if len(lista_csv) == 0:
        print ('Error: Pto. traf.:', id, 'No hay ficheros CSV de datos de tráfico')
        continue

    # carga trafico
    trafico = concat((read_csv(f, sep=';', index_col=1, parse_dates=True, header=None, names=('Id','Fecha','Intensidad','Ocupacion','Carga')) for f in lista_csv))
    trafico = trafico.resample('15min').ffill()

    # nuevo dataframe con precipitaciones, trafico, hora y marca de fin de semana 
    dataset = merge(precipitaciones, trafico, on='Fecha')
    dataset = merge(dataset, festivos, on='Fecha')
    dataset['Hora'] = dataset.index
    dataset['Hora'] = dataset['Hora'].dt.hour
    # trafico en la última columna, solo por comodidad
    dataset = dataset[['Precipitacion','Hora','Festivo','Intensidad']]
    dataset.sort_index(inplace=True)

    if dataset.shape[0] == 0:
        print ('Error: Pto. traf.:', id, 'No hay datos de tráfico tras cruzarlos con los de precipitaciones y festivos')
        continue
    
    # Desde la fecha de inicio se toman conf['numeroMuestras']  muestras
    # La ultima muestra se pierde en formateaMuestras
    dataset = dataset[to_datetime( conf['fechaInicio'] , unit='s'):]
    dataset = dataset[:conf['numeroMuestras'] + 1]

    if dataset.shape[0] < conf['numeroMuestras'] + 1 :
        print ('Error: Pto. traf.:', id, 'No hay', conf['numeroMuestras'], 'medidas de tráfico desde', to_datetime( conf['fechaInicio'] , unit='s'), 'Muestras:', dataset.shape[0])
        continue

    values = dataset.values
    values = values.astype('float32')

    # normalizacion de los valores
    scaler = MinMaxScaler(feature_range=(0, 1))
    values = scaler.fit_transform(values)

    # numero de tomas de entrada y valores de salida
    n_steps_in, n_steps_out = 3, 1
    # reformatea listas como entrada para el modelo
    values_X, values_y = formateaMuestras(values, n_steps_in, n_steps_out)
    n_input = values_X.shape[1] * values_X.shape[2]
    values_X = values_X.reshape((values_X.shape[0], n_input))

    datosJson = {"scalerMax": float(scaler.data_max_[-1]),
                 "scalerMin": float(scaler.data_min_[-1]),
                 "data": values_X.tolist() }

    with open(dir_salida + '/' + id + '.json', 'w') as f:
        json.dump(datosJson, f)
