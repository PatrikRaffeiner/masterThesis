# interpolate unstructured mesh data into structured pixel grid
# with excluded primitive geometry

import numpy as np
import pickle
import csv
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# Define size of output pixel grid
domsize = [1920,1024]


# Open the CSV file for reading
with open('test.csv', newline='') as file:

    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Create separate arrays to store the data
    x = []
    y = []
    Ux = []
    Uy = []
    p = []

    # skips the first line in the file (data description)
    next(csv_reader)

    # Loop through each row in the CSV file
    for row in csv_reader:

        # Store the data from each column in the appropriate array
        x.append(row[0])
        y.append(row[1])
        Ux.append(row[3])
        Uy.append(row[4])
        p.append(row[6])

# Create points of the original, unstructured mesh
points = np.column_stack((x,y))
points = points.astype(np.float64)

# Transform list into a numpy array of floats
p = np.array(p).astype(np.float64)
Ux = np.array(Ux).astype(np.float64)
Uy = np.array(Uy).astype(np.float64)

# Open the saved primitive geometry, needed to exclude correct 
# shape of pixels in grid
with open('ellipse.pkl', 'rb') as f:
    # Use pickle to deserialize and load the NumPy array
    ellipse = pickle.load(f)

# Create x and y components of grid
# Shape of primitive is excluded  
fluid_x = []
fluid_y = []
for xi in range(0,domsize[1]):
    for yi in range(0,domsize[0]):
        if ellipse[xi,yi] == 0:
            fluid_x.append(yi)
            fluid_y.append(xi)

# Actual interploation:
# points = nodes of unstructured mesh
# p = values of corresponding nodes
# (fluid_x, fluid_y) = structured grid with excluded primitive geometry
# method = nearest, also linear and cubic is possible
grid_p = griddata(points, p, (fluid_x, fluid_y), method='nearest')
grid_Ux = griddata(points, Ux, (fluid_x, fluid_y), method='nearest')
grid_Uy = griddata(points, Uy, (fluid_x, fluid_y), method='nearest')



# aligning interpolatied values to structured output grid (excluded primitive)
i = 0
p_ipol = np.empty((1920,1024))
Ux_ipol = np.empty((1920,1024))
Uy_ipol = np.empty((1920,1024))
for xi in range(0,domsize[1]):
    for yi in range(0,domsize[0]):
        if ellipse[xi,yi] == 0:
            p_ipol[yi,xi] = grid_p[i]
            Ux_ipol[yi,xi] = grid_Ux[i]
            Uy_ipol[yi,xi] = grid_Uy[i]
            i += 1


# dump interpolated solution 
with open('test_input_y.pkl', 'wb') as f:
        # stacking the generated arrays and expanding them by a leading dimension
        toDump = np.expand_dims(np.stack((Ux_ipol,Uy_ipol,p_ipol)), axis=0)
        # use pickle to serialize and save the NumPy array
        pickle.dump(toDump, f)


'''
plt.subplot(221)
plt.imshow(p_ipol.T, extent=(1,1920,1,1024), origin='lower')
plt.title('p')
plt.subplot(222)
plt.imshow(Ux_ipol.T, extent=(1,1920,1,1024), origin='lower')
plt.title('Ux')
plt.subplot(223)
plt.imshow(Uy_ipol.T, extent=(1,1920,1,1024), origin='lower')
plt.title('Uy')
plt.show()
'''