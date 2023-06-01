import PIL as PIL
from PIL import ImageDraw
import random
import snowy
import numpy as np
import pickle

from meshing_functions import *
from solving_functions import *
from interpolation_functions import *


def makePrim(args):

    # creating circle
    if len(args) == 4:
        # unwrapping the parameters
        type, diameter, imgsize, imgcenter = args

        # creating a new image (black)
        # mode "L" (8-bit pixels, grayscale)
        img = PIL.Image.new("L", imgsize, color=0)
        id = PIL.ImageDraw.Draw(img, mode="L")

        # drawing circle
        create_circle(id, imgcenter, diameter)

    # creating rectangle/iso_triangle/scalene_trinagle/ellipse/rounded_rectangle
    elif len(args) == 6:
        # unwrapping the parameters
        type, width, height, angle, imgsize, imgcenter = args

        # creating a new image (black)
        # mode "L" (8-bit pixels, grayscale)
        img = PIL.Image.new("L", imgsize, color=0)
        id = PIL.ImageDraw.Draw(img, mode="L")

        if type == "rectangle":
            create_rectangle(id, imgcenter, width, height)
        
        elif type == "iso_triangle":
            create_isoTriangle(id, imgcenter, width, height)
        
        elif type == "scalene_triangle":
            create_scaleneTriangle(id, imgcenter, width, height)
        
        elif type == "ellipse":
            # avoids creation of circles
            if width != height:
                create_ellipse(id, imgcenter, width, height)
            else:
                # return false for bad primitive
                return False

        elif type == "rounded_rectangle":
            create_roundedRectangle(id, imgcenter, width, height)

        img = img.rotate(angle)

    # creating pieslice/chord
    elif len(args) == 7:
        # unwrapping the parameters
        type, width, height, angle, chord_pie, imgsize, imgcenter = args

        # creating a new image (black)
        # mode "L" (8-bit pixels, grayscale)
        img = PIL.Image.new("L", imgsize, color=0)
        id = PIL.ImageDraw.Draw(img, mode="L")

        if type == "chord":
            if width != height:
                create_chord(id, imgcenter, width, height, chord_pie)
            else:
                # return false for bad primitive
                return False
            
        if type == "pieslice":
            create_pieslice(id, imgcenter, width, height, chord_pie)

        img = img.rotate(angle)

    np_prim = np.asarray(img)

    mesh_name, meshingSuccess = create_mesh(args, img)

    # catch meshing errors
    if meshingSuccess == True:
        inlet_vel = [10.0, 0.0]
        sim_time = 1000
        
        solvingSuccess = solve(mesh_name, inlet_vel, sim_time)

        # catch solving errors:
        if solvingSuccess == True:
            y_data = interpolate(mesh_name, np_prim, sim_time, imgsize)

            frc = create_flowRegionChannel(np_prim)
            sdf = create_SDF(np_prim)

            # creating an array that contains the x and y components of the inlet stream
            # x_comp = np.full(((imgsize[1]-2*padding), (imgsize[0]-2*padding)//2), inlet_vel[0]) 
            # y_comp = np.full(((imgsize[1]-2*padding), (imgsize[0]-2*padding)//2), inlet_vel[1]) 
            #vel_info = np.hstack((x_comp,y_comp))

            # creating a x-data bundle 
            x_data = np.stack((sdf.T, frc.T)) #, vel_info.T))

            # creating pickle output files
            pickle.dump(x_data, open("./solutions/" + mesh_name + "/x_data.pkl","wb")) 
            pickle.dump(y_data, open("./solutions/" + mesh_name + "/y_data.pkl","wb")) 
            
    
    return img



# functions to generate primitive images using  pillow (PIL)
def create_rectangle(id, center, width, height):
    id.rectangle([center[0] - round(width/2), center[1] - round(height/2), center[0] + round(width/2),
                  center[1] + round(height/2)], fill=255)


def create_roundedRectangle(id, center, width, height):
    short = min(width, height)
    r = short / 6
    id.rounded_rectangle([center[0] - round(width/2), center[1] - round(height/2), center[0] + round(width/2),
                  center[1] + round(height/2)], fill=255)


def create_circle(id, center, diameter):
    id.ellipse([center[0] - round(diameter/2), center[1] - round(diameter/2), center[0] + round(diameter/2),
                center[1] + round(diameter/2)], fill=255)


def create_isoTriangle(id, center, width, height):
    x1 = center[0] - round(width/2)
    x2 = center[0] + round(width/2)
    x3 = center[0]
    y1 = center[1] + round(height/2)
    y2 = center[1] + round(height/2)
    y3 = center[1] - round(height/2)
    id.polygon([x1, y1, x2, y2, x3, y3], fill=255)


def create_scaleneTriangle(id, center, width, height):
    x1 = center[0] - round(width/2 + 0.3*random.randrange(int(-width), int(width)))
    x2 = center[0] + round(width/2 + 0.3*random.randrange(int(-width), int(width)))
    x3 = center[0] + round(0.3*random.randrange(int(-width), int(width)))
    y1 = center[1] + round(height/2 + 0.3*random.randrange(int(-height), int(height)))
    y2 = center[1] + round(height/2 + 0.3*random.randrange(int(-height), int(height)))
    y3 = center[1] - round(height/2 + 0.3*random.randrange(int(-height), int(height)))
    id.polygon([x1, y1, x2, y2, x3, y3], fill=255)


def create_chord(id, center, width, height, chord_range):
    c_start = chord_range[0]
    c_end = chord_range[1]

    id.chord([center[0] - round(width/2), center[1] - round(height/2), center[0] + round(width/2),
              center[1] + round(height/2)], c_start, c_end, fill=255)


def create_pieslice(id, center, width, height, pie_range):
    p_start = 180 - pie_range[0]
    p_end = 185 + pie_range[1] 

    id.pieslice([center[0] - round(width/2), center[1] - round(height/2), center[0] + round(width/2),
              center[1] + round(height/2)], p_start, p_end, fill=255)


def create_ellipse(id, center, width, height):
    id.ellipse([center[0] - round(width/2), center[1] - round(height/2), center[0] + round(width/2),
              center[1] + round(height/2)], fill=255)


# function to create a flow region channel out of a nparray
# 0 = obstacle, 1 = fluid, 2 = inlet, 3 = outlet
def create_flowRegionChannel(img):

    # converting the image into a boolean array where the background (==0) 
    # is set to true and the foreground/obstacle to false
    frc = img == 0

    # converting the boolean array into a int array 
    frc = frc.astype(int)
    
    # setting edges of domain to inlet/outlet
    frc[0, :] = 3           # Upper domain side = outlet
    frc[-1, :] = 2          # lower domain side = inlet
    frc[:, 0] = 2           # left domain side = inlet
    frc[:, -1] = 3          # right domain side = outlet

    return frc


# Function to generate a Signed Distance Field out of a nparray
def create_SDF(img):

    # generating the SDF
    reshape = snowy.reshape(img)
    toUnshape = snowy.unitize(snowy.generate_sdf(reshape != 0.0))
    sdf = snowy.unshape(toUnshape)

    return sdf

