import PIL as PIL
import snowy
from PIL import ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, ceil
import random
#import pygmsh
#import gmsh
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
    num_prims = nparray.shape[0]

    print("Process finished!")
    print("Number of generated %ss:" %prim , num_prims)
    print("Number of suppressed circles: ", suppr_circles)
    print("Shape of %s-array:" %prim, nparray.shape)
    
    # returning 3D numpy array where 2D images are stacked, returning stack of images
    return nparray, img_stack,



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


# Function to generate a Signed Distance Field for every image of an image stack
def create_SDF(img_stack, padding):
    sdf_stack = []

    print("Creating SDF's... ")

    for img in img_stack:
        # crop padding 
        img = img[padding:-padding, padding:-padding]
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
def create_flowRegionChannel(img_stack, domsize, padding):
    frc_stack = []

    print("Creating flow region channels... ")

    # checking every pixel in every image of image list
    for img in img_stack:
        img = img[padding:-padding, padding:-padding]
        with np.nditer(img, op_flags=['readwrite']) as it:
            for px in it:
                if px == 0:         # setting black pixels to fluid domain (=0)
                    px[...] = 1

                else:
                    px[...] = 0     # setting white pixels to object domain (=1)

        img[0, :] = 4           # Upper domain side = outlet
        img[-1, :] = 3          # lower domain side = inlet
        img[:, 0] = 3           # left domain side = inlet
        img[:, -1] = 4          # right domain side = outlet

        frc_stack.append(img)

    frc_stack = np.asarray(frc_stack)

    print("Process finished")
    print("Number of FRC's: ", len(frc_stack))

    return frc_stack

# Function to generate a Signed Distance Field of wall boundaries
# This function is needed for the original DeepCFD input but will not be used 
# for the adapted version as no boundary walls are used
def create_wallSDF(domsize, stack, padding):
    # creating stack of wall-SDF's
    sdf_walls = []

    img = np.zeros((domsize[1]-padding, domsize[0]-padding))

    img[0, :] = 2       # Upper domain side = upper wall
    img[-1, :] = 1      # lower domain side = lower wall
    img = np.expand_dims(img, axis=0)

    wall_sdf = create_SDF(img)[0]

    for i in range(stack.shape[0]):
        sdf_walls.append(wall_sdf)

    sdf_walls = np.asarray(sdf_walls)
    sdf_walls.reshape((stack.shape[0], domsize[0], domsize[1]))

    return sdf_walls




