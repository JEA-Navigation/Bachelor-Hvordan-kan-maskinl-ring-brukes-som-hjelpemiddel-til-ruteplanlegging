import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Henter ut dataene fra .npy fila og legger de i en numpy-array
data_array = np.load('data.npy')

#Kaller første kolonne for easting, andre for northing og tredje for depth
easting, northing, depth = data_array[:,0], data_array[:,1], data_array[:,2]


#Plotter dataene ved hjelp av funksjonen scatter
plt.scatter(easting, northing)
plt.show()

