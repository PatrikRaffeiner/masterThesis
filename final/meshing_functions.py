import pygmsh
import gmsh
import numpy as np
from PIL import ImageFilter
import os


# Function to automatically create a fluid domain, load the primitive, define the boundarys
# and create a mesh with refined regions to fit as input for OpenFOAM
def meshing(edgecoords_, domsize, dest_path, msh_name):

    print("   Meshing...")
    
    edgeCoords = np.asarray(edgecoords_)
    edgeCoords = edgeCoords.astype(float)

    # swapping x and y coordinates to fit axis
    edgeCoords[:, [0, 1]] = edgeCoords[:, [1, 0]]


    # Instantiate geometry object
    with pygmsh.geo.Geometry() as geom:
        # Create polygon for airfoil
        mesh_size = 50       # general element size
        airfoil = geom.add_polygon(edgeCoords, make_surface=False)
        
        # create spline to smoothen curve
        '''
        s1 = geom.add_spline(edgeCoords)

        ll = geom.add_curve_loop([s1])
        airfoil = geom.add_plane_surface(ll)
        '''

        # create surface for numerical domain with an primitive-shaped hole
        xmin = 0.0  
        xmax = domsize[0] 
        ymin = 0.0 
        ymax = domsize[1]
        domainCoordinates = np.array(
            [[xmin, ymax, 0.0], [xmax, ymax, 0.0], [xmax, ymin, 0.0], [xmin, ymin, 0.0]]
        )   # bottom left,       bottom right,      top right,         top left

        # create line for downstream mesh refinement
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

        # conditions for boundary layer of primitive stored in list for every curve of primitive
        refinement_fields = []
        for curve in airfoil.curves:
            field = geom.add_boundary_layer(
                edges_list=[curve],
                lcmin=20, #lcmin=5
                lcmax=40,
                distmin=0.0,
                distmax=20,
            )
            refinement_fields.append(field)

        # create field for mesh refinement for downstrem of primitive
        downstream_field = geom.add_boundary_layer(
            edges_list=[downstream_line],
            lcmin=2,#lcmin=1,
            lcmax=50,
            distmin=0.1,
            distmax=520,
        )
        refinement_fields.append(downstream_field) 

        # create field for mesh refinement for upper wall
        '''upper_wall_field = geom.add_boundary_layer(
            edges_list=[upper_wall_line],
            lcmin=20, #lcmin=1,
            lcmax=50,
            distmin=0.1,
            distmax=520,
        )
        refinement_fields.append(upper_wall_field) 
        '''

        # create field for mesh refinement for lower wall
        '''lower_wall_field = geom.add_boundary_layer(
            edges_list=[lower_wall_line],
            lcmin=20, #lcmin=1,
            lcmax=50,
            distmin=0.1,
            distmax=520,
        )
        refinement_fields.append(lower_wall_field) 
        '''

        # boolean operator to extract airfoil from flow domain
        polygon = geom.add_polygon(domainCoordinates, holes=[airfoil])

        thickness = 2
        
        top, volume, lat = geom.extrude(polygon, [0, 0, thickness], num_layers=1, recombine=True)

        geom.add_physical(volume, label="volume")
        geom.add_physical([lat[2],lat[3]], label="inlet")
        geom.add_physical([lat[1],lat[0]], label="outlet")
        # removed wall lat[0],lat[2] to have "open" stream
        geom.add_physical([top,polygon], label="frontAndBack")

        geom.add_physical([*lat[5:]], label="primitive")

        geom.synchronize()


        # refine mesh based on the boundary-layer conditions 
        geom.set_background_mesh(refinement_fields, operator="Min")

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



# Edge detection to create edge list of generated primitive 
def edge_detection(img, domsize):
    edge_list = []
    
    print("   Detecting edges... ")

    # calculating edges using the laplacian kernel
    edge_img = img.filter(ImageFilter.Kernel((3, 3), (-1, -1, -1,
                                                          -1, 8, -1,
                                                          -1, -1, -1), 1, 0))


    edge = np.asarray(edge_img)

    coord_list = []  # list of lists containing coordinates (x,y) of all edge pixels

    # creating a list containing the edge pixels
    for y in range(0, domsize[0]):
        for x in range(0, domsize[1]):
            if edge[x, y] == 255:
                coord_list.append([x, y])

    edge_list.append(coord_list)  # contains the edge coordinates of all primitives  

    print("   Edge detected")

    # Returning an unordered edge list and a numpy array with a single edge line
    return edge_list, edge



# Function to order an unordered edge list of points by using region growing
# The output is a "drawable" list of points where a unfolded polygon can be created 
def region_growing(arr):
    # Find the first 1 in the array and perform region-growing on it
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i, j] != 0:
                start_pos = [i,j]
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
        #print(f"current pos: {current_pos[0]} {current_pos[1]}" )


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

    #print(len(output_list))
    return output_list



def create_meshes(domsize, revised_prims, 
                  rects=[], iso_tri=[], scl_tri=[], chrds=[], 
                  circls=[], ellps=[], pslices=[], rnd_rects=[]):
    
    prim_types = [chrds, circls, ellps, iso_tri, pslices, rects, rnd_rects, scl_tri]
    prim_names = ["chord", "circle", "ellipse", "iso_triangle", "pieslice", "rectangle", "rounded_rectangle", "scalene_triangle"]
    

    # creating a folder to store meshes
    dest_path = "./meshes"
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    # lists for failed primitives
    failed_mshs_list = []
    prim_count = 0

    # traversing through the different primitive types       
    for prims, prim_name in zip(prim_types, prim_names):
        # traversing through each primitive of the primitive types
        for i, prim in enumerate(prims):
            print("Processing: " + prim_name + str(i))
            print("prim count: " + str(prim_count))
            edge_list, edge_img = edge_detection(prim, domsize)

            ordered_edge_list = region_growing(edge_img)

            try: 
                meshing(ordered_edge_list, domsize, dest_path, prim_name + str(i))
                print("   Meshing finished")

            except Exception as e:
                failed_mshs_list.append(1)

                # adjust the nparray by deleting the primitives where the meshing failed 
                revised_prims = np.delete(revised_prims,prim_count, axis=0)
                print("ERROR:"  + str(e))
                print(prim_name + str(i) + " could not be meshed!")
            prim_count += 1
    print("Number of failed meshes: " + str(len(failed_mshs_list)))

    #prim_geom = np.asarray(prim_types)

    # adjust the nparray by deleting the primitives where the meshing failed 
    #prim_geom = np.delete(prim_geom,failed_mshs_list)
    return  np.asarray(revised_prims)

