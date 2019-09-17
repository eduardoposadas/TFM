#!/usr/bin/env python3
import sys
from math import sqrt
from numpy import array
from numpy import column_stack
from pandas import read_csv
from pandas import merge
from pandas import concat
from pandas import to_datetime
from matplotlib import pyplot
import matplotlib.dates as mdates
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense

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

if len(sys.argv) < 3:
    print ("Es necesario al menos un fichero de salida y un fichero de entrada.", file=sys.stderr)
    exit()

fichero_entrenamiento = sys.argv[1] + '_MLP_multivariante_entrenamiento.png'
fichero_prediccion = sys.argv[1] + '_MLP_multivariante_prediccion.png'
fichero_modelo = sys.argv[1] + '_MLP_multivariante_modelo.h5'

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

n_atrib = scaled.shape[1]
n_test_samples = 4 * 24 * 28 # 28 dias con 4 muestras por hora
n_train_samples = len(values) - n_test_samples
train = scaled[:n_train_samples, :]
test = scaled[n_train_samples:, :]

# numero de tomas de entrada y valores de salida
n_steps_in, n_steps_out = 3, 1
# reformatea listas como entrada para el modelo
train_X, train_y = formateaMuestras(train, n_steps_in, n_steps_out)
test_X, test_y = formateaMuestras(test, n_steps_in, n_steps_out)

n_input = train_X.shape[1] * train_X.shape[2]
train_X = train_X.reshape((train_X.shape[0], n_input))
test_X = test_X.reshape((test_X.shape[0], n_input))

# Definicion del modelo
model = Sequential()
model.add(Dense(24*4, activation='relu', input_dim=n_input))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(24*4, activation='relu'))
model.add(Dense(n_steps_out))
model.compile(optimizer='adam', loss='mse')

# Entrenamiento del modelo
history = model.fit(train_X, train_y, epochs=20, batch_size=100, validation_data=(test_X, test_y), verbose=0)

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

# Inversion del escalado de la prediccion
yprima_inv = column_stack([test_X[:,:(n_atrib-1)], yprima[:,0]])
yprima_inv = scaler.inverse_transform(yprima_inv)
yprima_inv = yprima_inv[:,-1]

# inversion del escalado de los datos reales
y_inv = column_stack([test_X[:,:(n_atrib-1)], test_y])
y_inv = scaler.inverse_transform(y_inv)
y_inv = y_inv[:,-1]

# dibuja la prediccion
fig, ax = pyplot.subplots(figsize=(15, 10))
pyplot.ylabel('Intensidad tráfico')
ax.plot(dataset.index[-len(y_inv):], y_inv, label='dato real')
ax.plot(dataset.index[-len(y_inv):], yprima_inv, label='predicción')
ax.legend()
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M'))
fig.autofmt_xdate(rotation=60)
pyplot.savefig(fichero_prediccion, bbox_inches='tight')
#pyplot.show()
pyplot.close()

# calcula RMSE
rmse = sqrt(mean_squared_error(y_inv, yprima_inv))
print('Test RMSE: %.3f' % rmse)
