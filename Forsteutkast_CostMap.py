import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d




data_array = np.load('data.npy')
#Teller baklengs [::-1] for å starte med første koordinater
Lat, Lon, Depth = data_array[::-1,0], data_array[::-1,1], data_array[::-1,2]

# Get X, Y, Z



X = Lat
Y = Lon
Z = Depth

#Plotter figuren basert på X, Y og Z

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', autoscale_on=True)
ax.plot_trisurf(X, Y, Z, color='white', edgecolors='grey', alpha=0.5)
ax.scatter(X, Y, Z, c='red')
plt.show()
