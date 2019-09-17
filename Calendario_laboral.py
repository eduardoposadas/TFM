#!/usr/bin/env python3

import pandas as pd

url = "https://datos.madrid.es/egob/catalogo/300082-0-calendario_laboral.csv"
df = pd.read_csv(url, encoding='latin-1', sep=';')

df['Dia'] = pd.to_datetime(df['Dia'], dayfirst=True)
df['Festivo'] = ((df['laborable / festivo / domingo festivo'] == 'festivo') |
                (df['Dia'].dt.dayofweek >= 5))

df = df[['Dia','Festivo']]

# Crea una entrada cada 15 min indicando si el dia es festivo
df.set_index('Dia', inplace = True)
df = df.resample('15min').ffill()

df.to_csv('festivos.csv', header=False)
