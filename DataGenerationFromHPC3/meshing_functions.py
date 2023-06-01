import pygmsh
import gmsh
import numpy as np
from PIL import ImageFilter
import signal

def timeout_handler(sinum, frame):
    raise TimeoutError("Exceeded meshing time!")

def create_mesh(args, img):

    # cases to unwrap arguments
    if len(args) == 4:
        # case circle
        type, diameter, imgsize, imgcenter = args

        # create a unique name for mesh
        mesh_name = type + "_" + str(diameter)

    elif len(args) == 6:
        # case rectangle/iso_triangle/scalene_trinagle/ellipse/rounded_rectangle
        type, width, height, angle, imgsize, imgcenter = args

        # create a unique name for mesh
        mesh_name = type + "_" + str(width) + "_" + str(height) + "_" + str(angle)

    elif len(args) == 7:
        # case pieslice/chord
        type, width, height, angle, chord_pie, imgsize, imgcenter = args

        # create a unique name for mesh
        mesh_name = type + "_" + str(width) + "_" + str(height) + "_" + str(angle) + "_" + str(chord_pie[0]) + "-" + str(chord_pie[1])

    # defining destination path to store mesh folder structure
    dest_path = "./meshes"

    # perform edge detection and region_growing on image to get
    # an unfolded polygon
    print("Edge detection " + mesh_name)
    edge_arr = edge_detection(img, imgsize)

    print("Region growing " + mesh_name)


    try:
        # setting the alarm to 20sec
        signal.alarm(20)
        ordered_edge_list = region_growing(edge_arr)
        signal.alarm(0)        
    
    
    except Exception as e:
        # handle all other exceptions
        print('{}: Polygon could not be detected from {}!'.format(e.__class__.__name__, mesh_name))
        signal.alarm(0) 
        success = False


    print("Meshing " + mesh_name)  

    # Defining the domain size 11 times bigger (5 * upstream, 5 * downstream)
    # This is to minimize boundary effects of the domain
    domsize = [imgsize[0] *11, imgsize[1]*11]


    # try to mesh geometry and catch exceptions & timeouts if duration is too long
    try:
        # setting the alarm to 10min
        signal.alarm(600)

        # run actual meshing
        meshing(ordered_edge_list, domsize, dest_path, mesh_name)
        signal.alarm(0)
        print("Meshing " + mesh_name + " successful")
        success = True

    except Exception as e:
        # handle all other exceptions
        print("ERROR:" + str(e))
        print(mesh_name +  " could not be meshed!")
        signal.alarm(0) 
        success = False

    return  mesh_name, success



# Edge detection to create edge list of generated primitive image
def edge_detection(img, domsize):
    edge_list = []

    # calculating edges using the laplacian kernel
    edge_img = img.filter(ImageFilter.Kernel((3, 3), (-1, -1, -1,
                                                      -1, 8, -1,
                                                      -1, -1, -1), 1, 0))

    edge = np.asarray(edge_img)

    # list of lists containing coordinates (x,y) of all edge pixels
    coord_list = []

    # creating a list containing the edge pixels
    for y in range(0, domsize[0]):
        for x in range(0, domsize[1]):
            if edge[x, y] == 255:
                coord_list.append([x, y])

    # contains the edge coordinates of all primitives
    edge_list.append(coord_list)

    # Returning a numpy array with a single edge line
    return edge


# Function to order an unordered edge list of points by using region growing
# The output is a "drawable" list of points where a unfolded polygon can be created
def region_growing(arr):

    # Find the first 1 in the array and perform region-growing on it
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i, j] != 0:
                start_pos = [i, j]
                break
        else:
            continue
        break


    # check if starting position does not create overlaps
    past_starting_pos = [start_pos]
    while True:
        flag = False
        num_neighbors = 0
        # Get the neighbors of the current pixel
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    neigh_pos = (start_pos[0]+i, start_pos[1]+j)
                    # Check if the neighbor is part of line and add to numcount if so
                    if arr[neigh_pos] != 0:
                        num_neighbors += 1
                        if flag != True and neigh_pos not in past_starting_pos:
                            first_neighbor = start_pos[0]+i, start_pos[1]+j
                            flag = True

        if num_neighbors < 3:
            break
        else:
            past_starting_pos.append(start_pos)
            start_pos = first_neighbor
            flag = False

    # Initialize the output list with the starting position
    output_list = []

    # Create a queue for the neighboring pixels to be processed
    queue = [start_pos]

    # Process the neighboring pixels until the queue is empty
    while len(queue) > 0:
        # Pop the first pixel from the queue
        current_pos = queue.pop(0)
        # print(f"current pos: {current_pos[0]} {current_pos[1]}" )

        # Get the neighbors of the current pixel
        for j in range(-1, 2):
            for i in range(-1, 2):
                # Calculate the position of the neighbor
                neighbor_pos = (current_pos[0]+i, current_pos[1]+j)

                # Check if the neighbor is part of line and hasn't been processed yet
                if arr[neighbor_pos] != 0 and neighbor_pos not in output_list:
                    # Add the neighbor to the output list and queue
                    output_list.append(neighbor_pos)
                    queue.append(neighbor_pos)
                    break
            else:
                continue
            break

    # print(len(output_list))
    return output_list




# Function to automatically create a fluid domain, load the primitive, define the boundaries
# and create a mesh with refined regions to fit as input for OpenFOAM
def meshing(edgecoords_, domsize, dest_path, msh_name): 
    
    edgeCoords = np.asarray(edgecoords_)
    edgeCoords = edgeCoords.astype(float)

    # swapping x and y coordinates to fit axis
    edgeCoords[:, [0, 1]] = edgeCoords[:, [1, 0]]


    # Instantiate geometry object
    with pygmsh.geo.Geometry() as geom:
        # Create polygon for airfoil
        mesh_size = 50       # general element size
        airfoil = geom.add_polygon(edgeCoords, make_surface=False)
        
        # create surface for numerical domain with a primitive-shaped hole
        # the size of the domain is 11 times the "image size", 
        # 5 lengths in up- and downstream direction & 5 heights above and below the primitive
        xmin = -domsize[0] * 5/11
        xmax = domsize[0] * 6/11
        ymin = -domsize[1] * 5/11 
        ymax = domsize[1] * 6/11
        domainCoordinates = np.array(
            [[xmin, ymax, 0.0], [xmax, ymax, 0.0], [xmax, ymin, 0.0], [xmin, ymin, 0.0]]
        )   # bottom left,       bottom right,      top right,         top left


        # create line for downstream mesh refinement, 
        # from the middle of the trailing edge's primitive to the boundary of the domain
        d_x1 = edgeCoords[:, 0].max()
        d_y1 = (edgeCoords[:, 1].max()-edgeCoords[:, 1].min())/2 + edgeCoords[:, 1].min()
        d_x2 = xmax
        d_y2 = d_y1
        d_points = [geom.add_point([d_x1,d_y1]), geom.add_point([d_x2,d_y2])]
        downstream_line = geom.add_line(*d_points)

        '''
        # create line for upper wall mesh refinement
        u_points = [geom.add_point([xmax, ymin]), geom.add_point([xmin, ymin])]
        upper_wall_line = geom.add_line(*u_points)
        
        # create line for lower wall mesh refinement
        l_points = [geom.add_point([xmin, ymax]), geom.add_point([xmax, ymax])]
        lower_wall_line = geom.add_line(*l_points)

        # create line for inlet condition
        i_points = [geom.add_point([xmin, ymax]), geom.add_point([xmin, ymin])]
                                 # bottom left                    top left
        inlet_line = geom.add_line(*i_points)
        #inlet = geom.add_physical(inlet_line, label = "inlet")
        '''

        # conditions for the mesh refinement of the boundary layer of the primitive,
        # stored as a list of every curve of the primitive
        refinement_fields = []
        for curve in airfoil.curves:
            field = geom.add_boundary_layer(
                edges_list=[curve],
                lcmin=0.07,
                lcmax=70,
                distmin=0.0,
                distmax=7,
            )
            refinement_fields.append(field)

        # conditions for the mesh refinement downstream of the primitive
        downstream_field = geom.add_boundary_layer(
            edges_list=[downstream_line],
            lcmin=0.35,
            lcmax=50,
            distmin=0.0,
            distmax=350,
        )
        refinement_fields.append(downstream_field) 

        # boolean operator to extract airfoil from flow domain
        polygon = geom.add_polygon(domainCoordinates, holes=[airfoil])

        # extruding the 2D flow domain with the primitive shaped hole into a 3D mesh with a single layer thickness of 2
        # this needs to be done because OpenFoam cannot handle real 2D inputs
        thickness = 2
        top, volume, lat = geom.extrude(polygon, [0, 0, thickness], num_layers=1, recombine=True)

        # Add physical properties and labels to the extruded surfaces/volumes
        geom.add_physical(volume, label="volume")
        geom.add_physical([lat[2],lat[3]], label="inlet")
        geom.add_physical([lat[1],lat[0]], label="outlet")
        geom.add_physical([top,polygon], label="frontAndBack")
        geom.add_physical([*lat[5:]], label="primitive")

        geom.synchronize()


        # refine mesh based on the boundary-layer conditions 
        geom.set_background_mesh(refinement_fields, operator="Min")

        # Actual meshing
        mesh = geom.generate_mesh()

        # recombination of elements to produce quadrilateral element
        #geom.set_recombined_surfaces([polygon.surface])

        #optimized_mesh = pygmsh.optimize(mesh, method="")

        # Write mesh to OpenFOAM format
        gmsh.write(dest_path + "/" + msh_name + ".msh2")
        gmsh.option.setNumber("Mesh.SaveAll", True)
        gmsh.option.setNumber("Mesh.SaveGroupsOfNodes", True)
        gmsh.option.setNumber("Mesh.SaveGroupsOfElements", True)

        # Run gmsh GUI to check meshing
        #gmsh.fltk.run()

    return mesh


