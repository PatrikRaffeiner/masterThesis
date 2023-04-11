
import subprocess
import numpy as np
from scipy.interpolate import griddata




# interpolate unstructured mesh data into structured pixel grid
# with excluded primitive geometry
def interpolate(mesh_name, prim_arr, sim_time, domsize, padding):

    # Set the source path to the current solution folder
    src_path = "./solutions/" + mesh_name

    # write the cell centres of the mesh into a seperate file via foam postprocessing
    write_cell_centres(src_path)

    # extract the cell coordinates and the corresponding pressure, x & y velocities
    cell_coords = get_cell_coords(src_path, sim_time)
    p = get_pressure(src_path, sim_time)
    Ux, Uy = get_velocities(src_path, sim_time) 

    # create x and y grids with excluded shape of primitive
    fluid_x = []
    fluid_y = []
    for xi in range(0,domsize[1]):
        for yi in range(0,domsize[0]):
            if prim_arr[xi,yi] == 0:
                fluid_x.append(yi)
                fluid_y.append(xi)


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
            if prim_arr[xi,yi] == 0:
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

    return bundle




# function to execute the OpenFoam post processing function writeCellCentres
# that writes the cell centres of the mesh into a seperate file
def write_cell_centres(src_path):
    # Define command to write cell centres
    command = ["simpleFoam", "-postProcess", "-func", "writeCellCentres", "-case" , src_path]

    # Run writeCellCentres
    subprocess.check_call(command, stdout=subprocess.DEVNULL)



# function to extract the cell coordinates from a generated "C"-file
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



# function to extract velocities of direction x and y
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



# function to extract the pressure
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
            
            



