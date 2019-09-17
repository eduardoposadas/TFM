#!/usr/bin/env python3
import sys
import glob
import json
from pandas import read_csv
from pandas import merge
from pandas import DataFrame
from pandas import concat
from pandas import to_datetime
from sklearn.preprocessing import MinMaxScaler

dir_salida = './MuestrasLSTM'
dir_datos='./Datos/*/'

# formatea para modelo
def formateaMuestras(muestras, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(muestras) is list else muestras.shape[1]
	df = DataFrame(muestras)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg

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
    print('Generando fichero JSON con muestras para predicción web LSTM para pto. medida:', id)
    
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
    # Pasa los valores a punto flotante
    values = values.astype('float32')
    # normalizacion de los valores
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)
    # reformatea listas como entrada para el modelo
    reframed = formateaMuestras(scaled, 1, 1)
 
    # dividir datos de entrenamiento y validacion
    values = reframed.values
    values_X = values[:, :-1]
    values_X = values_X.reshape((values_X.shape[0], 1, values_X.shape[1]))

    datosJson = {"scalerMax": float(scaler.data_max_[-1]),
                 "scalerMin": float(scaler.data_min_[-1]),
                 "data": values_X.tolist() }

    with open(dir_salida + '/' + id + '.json', 'w') as f:
        json.dump(datosJson, f)
