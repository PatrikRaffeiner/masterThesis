# interpolate mesh data into pixel grid

import numpy as np
from scipy.interpolate import griddata

pointFile = open("points",'r')
Lines = pointFile.readlines()

num_points = Lines[18]



print(Lines[18])