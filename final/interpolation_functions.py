# interpolate unstructured mesh data into structured pixel grid
# with excluded primitive geometry

import numpy as np
import os
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import subprocess
import pickle


def write_cell_centres(src_path):
    # Define command to write cell centres
    command = ["simpleFoam", "-postProcess", "-func", "writeCellCentres", "-case" , src_path]

    # Run writeCellCentres
    subprocess.check_call(command)



def interpolate(prim_geom, sim_time, domsize, padding):
    # Set directory where all solutions are located
    solv_dir =  "./solutions"

    # Get a list of all files in the solution folder
    solutions = os.listdir(solv_dir)

    # Sort the list by alphabetic order 
    solutions = sorted(solutions)

    # Create an empty list for final output data
    toDump = [] 

    # Iterate over the files in solution folder
    for solution, prim in zip(solutions, prim_geom):
        print("Processing " + solution)

        # Set the source path to the current solution folder
        src_path = solv_dir + "/" + solution

        write_cell_centres(src_path)

        cell_coords = get_cell_coords(src_path, sim_time)
        p = get_pressure(src_path, sim_time)
        Ux, Uy = get_velocities(src_path, sim_time) 

        # Create x and y components of grid
        # Shape of primitive is excluded  
        fluid_x = []
        fluid_y = []
        for xi in range(0,domsize[1]):
            for yi in range(0,domsize[0]):
                if prim[xi,yi] == 0:
                    fluid_x.append(yi)
                    fluid_y.append(xi)
        
        print("Interpolating...")

        # Actual interploation:
        # points = nodes of unstructured mesh
        # p = values of corresponding nodes
        # (fluid_x, fluid_y) = structured grid with excluded primitive geometry
        # method = nearest, also linear and cubic is possible
        grid_p = griddata(cell_coords, p, (fluid_x, fluid_y), method='cubic')
        grid_Ux = griddata(cell_coords, Ux, (fluid_x, fluid_y), method='cubic')
        grid_Uy = griddata(cell_coords, Uy, (fluid_x, fluid_y), method='cubic')
        
        # aligning interpolated values to structured output grid (excluded primitive)
        i = 0
        p_ipol = np.zeros((domsize[0],domsize[1]))
        Ux_ipol = np.zeros((domsize[0],domsize[1]))
        Uy_ipol = np.zeros((domsize[0],domsize[1]))
        for xi in range(0,domsize[1]):
            for yi in range(0,domsize[0]):
                if prim[xi,yi] == 0:
                    p_ipol[yi,xi] = grid_p[i]
                    Ux_ipol[yi,xi] = grid_Ux[i]
                    Uy_ipol[yi,xi] = grid_Uy[i]
                    i += 1
                else:
                    p_ipol[yi,xi] = np.nan
                    Ux_ipol[yi,xi] = np.nan
                    Uy_ipol[yi,xi] = np.nan
                     
        
        # crop the generated arrays (due to cubic interpolation) 
        Ux_ipol = Ux_ipol[padding:-padding, padding:-padding]
        Uy_ipol = Uy_ipol[padding:-padding, padding:-padding]
        p_ipol = p_ipol[padding:-padding, padding:-padding]

        # stacking the generated arrays
        bundle = np.stack((Ux_ipol.T,Uy_ipol.T,p_ipol.T))
        toDump.append(bundle)


    toDump = np.asarray(toDump)
    print(toDump.shape)


    # dump interpolated solution 
    with open('test_input_y.pkl', 'wb') as f:
            # stacking the generated arrays and expanding them by a leading dimension
            #toDump = np.expand_dims(np.stack((Ux_ipol,Uy_ipol,p_ipol)), axis=0)
            # use pickle to serialize and save the NumPy array
            pickle.dump(toDump, f)
    

        
        


def get_cell_coords(src_path, sim_time):
    # Initialize empty lists for the coordinates
    x = []
    y = []
    z = []

    # Load the coordinates of mesh points
    with open(src_path + "/" + str(sim_time) + "/C","r") as point_file:
        # Skip the first lines (header)
        for _ in range(20):
            next(point_file)

        # Read the number of coordinates from the first line after the header
        num_lines = int(next(point_file).strip())
        #print(num_coords)

        # Skip the bracket line
        next(point_file)

        # Loop over the remaining lines and extract the coordinates
        for line, count in zip(point_file,range(num_lines)):
            # Strip the brackets and split the line into a tuple of strings
            coord = line.strip('()\n').split()

            # Append the coordinates to the corresponding lists
            x.append(coord[0])
            y.append(coord[1])
            z.append(coord[2])

        # Create points of the original, unstructured mesh
        cells = np.column_stack((x,y))
        cells = cells.astype(np.float64) 

    return cells   


def get_velocities(src_path, sim_time):
    # Initialize empty lists for the velocities
    Ux = []
    Uy = []
    Uz = []

    # Load the velocities of the solution
    with open(src_path + "/" + str(sim_time) + "/U","r") as vel_file:
        # Skip the first lines (header)
        for _ in range(20):
            next(vel_file)

        # Read the number of lines from the first line after the header
        num_lines = int(next(vel_file).strip())

        # Skip the bracket line
        next(vel_file)

        # Loop over the remaining lines and extract the velocities
        for line, count in zip(vel_file,range(num_lines)):
            # Strip the brackets and split the line into a tuple of strings
            vel = line.strip('()\n').split()

            # Append the coordinates to the corresponding lists
            Ux.append(vel[0])
            Uy.append(vel[1])
            Uz.append(vel[2])
        
        # Transform velocities into correct format
        Ux = np.array(Ux).astype(np.float64)
        Uy = np.array(Uy).astype(np.float64)

    return Ux, Uy 


def get_pressure(src_path, sim_time):
    # Initialize empty lists for the pressure
    p = []

    # Load the pressure of the solution
    with open(src_path + "/" + str(sim_time) + "/p","r") as p_file:
        # Skip the first lines (header)
        for _ in range(20):
            next(p_file)

        # Read the number of lines from the first line after the header
        num_lines = int(next(p_file).strip())

        # Skip the bracket line
        next(p_file)

        # Loop over the remaining lines and extract the velocities
        for line, count in zip(p_file,range(num_lines)):
            # Strip the brackets and split the line into a tuple of strings
            press = line.strip('\n')

            # Append the coordinates to the corresponding lists
            p.append(press)
        
        # Transform velocities into correct format
        p = np.array(p).astype(np.float64)

    return p
            
            



