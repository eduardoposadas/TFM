#!/usr/bin/python3
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import csv


if len(sys.argv) < 2:
    print ("Es necesario el nombre de un fichero.")
    exit()

f = sys.argv[1]

x = []
y = []

with open(f, 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=';')
    for row in plots:
        x.append(datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S'))
        y.append(int(row[2]))

plt.plot(x,y, label='Intensidad')
plt.xlabel('Fecha')
plt.ylabel('Intensidad')
plt.title('Intensidad\n' + f)
plt.legend()
plt.gcf().autofmt_xdate()
plt.show()
