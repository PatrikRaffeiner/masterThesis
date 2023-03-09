import PIL as PIL
import snowy
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, ceil
import random
import pygmsh
import gmsh
from helpers import compute_volume

# function to calculate the step size of height, width or angle between boundaries
def calc_divisions(lower, upper, div):
    if div == 1:
        return upper - lower
    else:
        step_size = (upper - lower) / (div - 1)
        return step_size


# function to create a numpy-array & array-stack with primitives of size domsize x domsize
# the number of images is set by the corresponding divisions
# the divisions that set the number of separations between the to be generated width,
# height and angle are mandatory for every primitive
# additional arguments must be passed to generate chords and pie slices
def create_primitive_stack(prim, domsize, domcenter, height_div, width_div, angle_div,
                         chord_div=0, pie_div=0):
    # Ranges of the smallest/biggest dimensions of the primitive
    height_range = (150, 400) # good range for 1024p 150, 400
    width_range = (150, 400)  # good range for 1024p 150, 400
    angle_range = (-15, 15)

    # Exception if no chord division is assigned
    if prim == "chord":
        if chord_div == 0:
            raise Exception("Chord divisions not assigned. Please assign: chord_div = -value-.")
        chord_range = (180, 280)
        chord_step = calc_divisions(chord_range[0], chord_range[1], chord_div)

    # Exception if no pieslice division is assigned
    if prim == "pieslice":
        if pie_div == 0:
            raise Exception("Piesclice divisions not assigned. Please assign: pie_div = -value-.")
        pie_range = (25, 160)
        pie_step = calc_divisions(pie_range[0], pie_range[1], pie_div)

    # Assigning the ranges withing primitives are generated 
    width_step = calc_divisions(width_range[0], width_range[1], width_div)
    height_step = calc_divisions(height_range[0], height_range[1], height_div)
    angle_step = calc_divisions(angle_range[0], angle_range[1], angle_div)

    img_stack = []
    imgarray_stack = []
    suppr_circles = 0       # supressed circles when generating ellipses (height = width)

    print("Creating %ss ..." % prim)

    # Creating primitives with different heights, widths, angles (& chords, pie slices)
    for h in range(height_div):
        primheight = height_range[0] + height_step * h

        if prim != "circle":  # avoids rotating circles

            for w in range(width_div):
                primwidth = width_range[0] + width_step * w

                for a in range(angle_div):
                    angle = angle_range[0] + angle_step * a

                    # creating a new image (black)
                    img = PIL.Image.new("L", domsize, color=0)

                    # drawing primitive
                    id = PIL.ImageDraw.Draw(img, mode="L")  # mode "L" (8-bit pixels, grayscale)

                    if prim == "rectangle":
                        create_rectangle(id, domcenter, primwidth, primheight)
                        rotate_and_stack(img, angle, img_stack, imgarray_stack)

                    elif prim == "iso_triangle":
                        create_isoTriangle(id, domcenter, primwidth, primheight)
                        rotate_and_stack(img, angle, img_stack, imgarray_stack)

                    elif prim == "scalene_triangle":
                        create_scaleneTriangle(id, domcenter, primwidth, primheight)
                        rotate_and_stack(img, angle, img_stack, imgarray_stack)

                    elif prim == "chord":
                        if primwidth != primheight:
                            for c in range(chord_div):
                                create_chord(id, domcenter, primwidth, primheight, chord_range, chord_step, c)
                                rotate_and_stack(img, angle, img_stack, imgarray_stack)

                    elif prim == "ellipse":
                        if primwidth != primheight:
                            create_ellipse(id, domcenter, primwidth, primheight)
                            rotate_and_stack(img, angle, img_stack, imgarray_stack)

                        else:
                            suppr_circles += 1

                    elif prim == "pieslice":
                        for p in range(pie_div):
                            create_pieslice(id, domcenter, primwidth, primheight, pie_range, pie_step, p)
                            rotate_and_stack(img, angle, img_stack, imgarray_stack)

                    elif prim == "rounded_rectangle":
                        create_roundedRectangle(id, domcenter, primwidth, primheight)
                        rotate_and_stack(img, angle, img_stack, imgarray_stack)

                    else:
                        raise Exception("Primitive not found. Please try: rectangle, iso_triangle, ellipse, circle, ...")


        else:  # creating circles
            # creating a new image (black)
            img = PIL.Image.new("L", domsize, color=0)

            # drawing primitive
            id = PIL.ImageDraw.Draw(img, mode="L")  # mode "L" (8-bit pixels, grayscale)

            create_circle(id, domcenter, primheight)

            # converting image (PNG) to numpy array
            imgarray = np.asarray(img)

            img_stack.append(img)
            imgarray_stack.append(imgarray)

    # transforming list of images into a numpy array
    nparray = np.asarray(imgarray_stack)

    print("Process finished!")
    print("Number of generated %ss:" %prim , nparray.shape[0])
    print("Number of suppressed circles: ", suppr_circles)
    print("Shape of %s-array:" %prim, nparray.shape)
    
    # returning 3D numpy array where 2D images are stacked, returning stack of images
    return nparray, img_stack



# function to rotate images and add it to list
def rotate_and_stack(img, angle, img_stack, imgarray_stack):
    img = img.rotate(angle)

    # converting image (PNG) to numpy array
    imgarray = np.asarray(img)

    img_stack.append(img)
    imgarray_stack.append(imgarray)

# functions to generate primitive images using  pillow (PIL)
def create_rectangle(id, center, width, height):
    id.rectangle([center[0] - width / 2, center[1] - height / 2, center[0] + width / 2,
                  center[1] + height / 2], fill=255)


def create_roundedRectangle(id, center, width, height):
    short = min(width, height)
    r = short / 6
    id.rounded_rectangle([center[0] - width / 2, center[1] - height / 2, center[0] + width / 2,
                          center[1] + height / 2], radius=r, fill=255)


def create_circle(id, center, diameter):
    id.ellipse([center[0] - diameter / 2, center[1] - diameter / 2, center[0] + diameter / 2,
                center[1] + diameter / 2], fill=255)


def create_isoTriangle(id, center, width, height):
    x1 = center[0] - width/2
    x2 = center[0] + width/2
    x3 = center[0]
    y1 = center[1] + height/2
    y2 = center[1] + height/2
    y3 = center[1] - height/2
    id.polygon([x1, y1, x2, y2, x3, y3], fill = 255)


def create_scaleneTriangle(id, center, width, height):
    x1 = center[0] - width/2 + 0.3*random.randrange(int(-width), int(width))
    x2 = center[0] + width/2+ 0.3*random.randrange(int(-width), int(width))
    x3 = center[0] + 0.3*random.randrange(int(-width), int(width))
    y1 = center[1] + height/2 + 0.3*random.randrange(int(-height), int(height))
    y2 = center[1] + height/2 + 0.3*random.randrange(int(-height), int(height))
    y3 = center[1] - height/2 + 0.3*random.randrange(int(-height), int(height))
    id.polygon([x1, y1, x2, y2, x3, y3], fill = 255)


def create_chord(id, center, width, height, chord_range, step, c):
    c_start = chord_range[0] - step * c
    c_end = chord_range[1] + step * c

    id.chord([center[0] - width / 2, center[1] - height / 2, center[0] + width / 2,
              center[1] + height / 2], c_start, c_end, fill=255)


def create_ellipse(id, center, width, height):
    id.ellipse([center[0] - width / 2, center[1] - height / 2, center[0] + width / 2,
                center[1] + height / 2], fill=255)


def create_pieslice(id, center, width, height, pie_range, step, p):
    p_start = 180- pie_range[0] - step * p
    p_end = 185 + pie_range[0] + step * p

    id.pieslice([center[0] - width / 2, center[1] - height / 2, center[0] + width / 2,
                 center[1] + height / 2], p_start, p_end, fill=255)


def plot_np_array(np_array, title):
    plt.figure()
    plt.title(title)
    plt.imshow(np_array)
    plt.show()


# only for visualization
# do not use for big arrays!
def plot_np_arrays(np_array, title):
    plt.title(title)
    fig = plt.gcf()
    fig.set_size_inches(10, 10)
    for i in range(np_array.shape[0]):
        plt.subplot(ceil(sqrt(np_array.shape[0])), ceil(sqrt(np_array.shape[0])), i + 1)
        plt.axis('off')
        plt.imshow(np_array[i])

    plt.tight_layout()
    plt.show()

# Edge detection to create edge list of generated primitive 
def edge_detection(stack, domsize):
    edge_list = []

    print("Detecting edges... ")

    for img in stack:
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

    print("Process finished!")
    print("Number of edges detected: ", len(edge_list))

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



# Function to generate a Signed Distance Field for every image of an image stack
def create_SDF(img_stack):
    sdf_stack = []

    print("Creating SDF's... ")

    for img in img_stack:
        reshape = snowy.reshape(img)
        toUnshape = snowy.unitize(snowy.generate_sdf(reshape != 0.0))
        sdf = snowy.unshape(toUnshape)
        sdf_stack.append(sdf)

    print("Process finished")
    print("Number of SDF's: ", len(sdf_stack))

    sdf_stack = np.asarray(sdf_stack)

    return sdf_stack


# function to create a flow region channel with
# 0 = obstacle, 1 = fluid, 2 = wall, 3 = inlet, 4 = outlet
def create_flowRegionChannel(img_stack, domsize):
    frc_stack = []

    print("Creating flow region channels... ")

    # checking every pixel in every image of image list
    for img in img_stack:
        with np.nditer(img, op_flags=['readwrite']) as it:
            for px in it:
                if px == 0:         # setting black pixels to fluid domain (=0)
                    px[...] = 1

                else:
                    px[...] = 0     # setting white pixels to object domain (=1)

        img[0, :] = 2               # Upper domain side = upper wall
        img[domsize[1] - 1, :] = 2  # lower domain side = lower wall
        img[:, 0] = 3               # left domain side = inlet
        img[:, domsize[0] - 1] = 4  # right domain side = outlet

        frc_stack.append(img)

    frc_stack = np.asarray(frc_stack)

    print("Process finished")
    print("Number of FRC's: ", len(frc_stack))

    return frc_stack

# Function to generate a Signed Distance Field of wall boundaries
# This function is needed for the original DeepCFD input but will not be used 
# for the adapted version as no boundary walls are used
def create_wallSDF(domsize, stack):
    # creating stack of wall-SDF's
    sdf_walls = []

    img = np.zeros((domsize[1], domsize[0]))

    img[0, :] = 2  # Upper domain side = upper wall
    img[domsize[1] - 1, :] = 1  # lower domain side = lower wall
    img = np.expand_dims(img, axis=0)

    wall_sdf = create_SDF(img)[0]

    for i in range(stack.shape[0]):
        sdf_walls.append(wall_sdf)

    sdf_walls = np.asarray(sdf_walls)
    sdf_walls.reshape((stack.shape[0], domsize[0], domsize[1]))

    return sdf_walls


# Function to automatically create a fluid domain, load the primitive, define the boundarys
# and create a mesh with refined regions to fit as input for OpenFOAM
def meshing(edgecoords_, domsize):
    
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
        gmsh.write("my_model.msh")
        gmsh.option.setNumber("Mesh.SaveAll", True)
        gmsh.option.setNumber("Mesh.SaveGroupsOfNodes", True)
        gmsh.option.setNumber("Mesh.SaveGroupsOfElements", True)

        # Run gmsh GUI to check meshing
        #gmsh.fltk.run()

    return mesh


