#!/usr/bin/env python3
import sys
from math import sqrt
from numpy import column_stack
from matplotlib import pyplot
import matplotlib.dates as mdates
from pandas import read_csv
from pandas import merge
from pandas import DataFrame
from pandas import concat
from pandas import to_datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
 
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

if len(sys.argv) < 3:
    print ("Es necesario al menos un fichero de salida y un fichero de entrada.", file=sys.stderr)
    exit()

fichero_entrenamiento = sys.argv[1] + '_LSTM_multivariante_entrenamiento.png'
fichero_prediccion = sys.argv[1] + '_LSTM_multivariante_prediccion.png'
fichero_modelo = sys.argv[1] + '_LSTM_multivariante_modelo.h5'

# carga trafico
trafico = concat((read_csv(f, sep=';', index_col=1, parse_dates=True, header=None, names=('Id','Fecha','Intensidad','Ocupacion','Carga')) for f in sys.argv[2:]))

# carga precipitaciones
precipitaciones = read_csv('precipitaciones.csv', header=None, names=('Fecha','Precipitacion'))
precipitaciones['Fecha'] = to_datetime(precipitaciones['Fecha'], dayfirst=True)
precipitaciones.drop_duplicates(inplace=True)
precipitaciones.set_index('Fecha', inplace=True)
precipitaciones = precipitaciones.resample('15min').ffill()

# carga festivos
festivos = read_csv('festivos.csv', index_col=0, parse_dates=True, header=None, names=('Fecha','Festivo'))

# nuevo dataframe con precipitaciones, trafico, hora y marca de fin de semana 
dataset = merge(precipitaciones, trafico, on='Fecha')
dataset = merge(dataset, festivos, on='Fecha')
dataset['Hora'] = dataset.index
dataset['Hora'] = dataset['Hora'].dt.hour
# trafico en la última columna, solo por comodidad
dataset = dataset[['Precipitacion','Hora','Festivo','Intensidad']]
dataset.sort_index(inplace=True)

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
n_atrib = dataset.shape[1]
n_test_samples = 4 * 24 * 28 # 28 dias con 4 muestras por hora
#n_train_samples = 365 * 24 * 4
n_train_samples = len(values) - n_test_samples
train = values[:n_train_samples, :]
test = values[n_train_samples:, :]
# dividir entre entradas y salidas
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
# reformatea a tensores 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)
 
# Definicion del modelo
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mse', optimizer='adam')

# Entrenamiento del modelo
history = model.fit(train_X, train_y, epochs=30, batch_size=100, validation_data=(test_X, test_y), verbose=2, shuffle=False)

# Guarda el modelo entrenado
model.save(fichero_modelo)

# Dibuja el historial del entrenamiento del modelo
pyplot.xlabel('Época')
pyplot.ylabel('Valor de 0 a 1')
pyplot.plot(history.history['loss'], label='entrenamiento')
pyplot.plot(history.history['val_loss'], label='validación')
pyplot.legend()
pyplot.grid(True)
pyplot.savefig(fichero_entrenamiento, bbox_inches='tight')
#pyplot.show()
pyplot.close()
 
# prediccion
yprima = model.predict(test_X)
test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
# Inversion del escalado de la prediccion
yprima_inv = column_stack([test_X[:,:(n_atrib-1)], yprima[:,0]])
yprima_inv = scaler.inverse_transform(yprima_inv)
yprima_inv = yprima_inv[:,-1]
# Inversion del escalado de los datos reales
test_y = test_y.reshape((len(test_y), 1))
inv_y = column_stack([test_X[:,:(n_atrib-1)], test_y])
inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,-1]

# dibuja la prediccion
fig, ax = pyplot.subplots(figsize=(15, 10))
pyplot.ylabel('Intensidad tráfico')
ax.plot(dataset.index[-len(inv_y):], yprima_inv, label='predicción')
ax.plot(dataset.index[-len(inv_y):], inv_y, label='dato real')
ax.legend()
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M'))
fig.autofmt_xdate(rotation=60)
pyplot.savefig(fichero_prediccion, bbox_inches='tight')
#pyplot.show()
pyplot.close()

# calcula RMSE
rmse = sqrt(mean_squared_error(inv_y, yprima_inv))
print('Test RMSE: %.3f' % rmse)
