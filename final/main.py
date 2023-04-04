# This script and the dedicated subscript is to generate 2D primitives
# of various shape and position, create an unstructured mesh to serve as an input file for OpenFOAM,
# and create a Signed Distance Field to serve as an input file for the DeepCFD neuronal network

# Owned and developed by Patrik Raffeiner
# Developed in the course of a master thesis at the Management Center Innsbruck

from primgen_functions import *
from meshing_functions import *
from solving_functions import *
from interpolation_functions import *
import pickle


import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # setting size of domain for all primitives
    imgsize = (1920, 1024)      # row-major order
    padding = 20                # padding to be removed along image edge (cubic interpolation) 
    domsize = (imgsize[0] + 2*padding, imgsize[1] + 2*padding)

    domcenter = (int(domsize[0] / 2), int(domsize[1] / 2))
    
    # generating ellipses
    ellipses_geom, img_stack_ellipses = create_primitive_stack("ellipse", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4)
    
    # generating rectangles
    rects_geom, img_stack_rects = create_primitive_stack("rectangle", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4)
   
    # generating isometric triangles
    iso_tri_geom, img_stack_iso_tri = create_primitive_stack("iso_triangle", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4)
   
    # generating scalene triangles
    scal_tri_geom, img_stack_scal_tri = create_primitive_stack("scalene_triangle", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4)
   
    # generating chords
    chord_geom, img_stack_chord = create_primitive_stack("chord", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4, chord_div=3)
   
    # generating pieslices
    pieslice_geom, img_stack_pieslice = create_primitive_stack("pieslice", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4, pie_div=3)
    
    # generating rounded rectangles
    rnd_rects_geom, img_stack_rnd_rects = create_primitive_stack("rounded_rectangle", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4)
    
    # generating rounded rectangles
    circl_geom, img_stack_circl = create_primitive_stack("circle", domsize, domcenter, height_div=4,
                                                               width_div=4, angle_div=4)
    
   

    # merging geometries for mesh interpolation
    prim_geom = np.vstack((ellipses_geom, rects_geom,
                           iso_tri_geom, scal_tri_geom, 
                           chord_geom, pieslice_geom,
                           rnd_rects_geom, circl_geom))
    
    img_stack_prim = img_stack_ellipses + img_stack_rects+ img_stack_iso_tri + img_stack_scal_tri  + img_stack_chord + img_stack_pieslice + img_stack_rnd_rects +img_stack_circl

    # creating the pygmsh-meshes for the geometries
    prim_geom = create_meshes(domsize, prim_geom, 
                              ellps = img_stack_ellipses, 
                              rects= img_stack_rects,
                              iso_tri=img_stack_iso_tri,
                              scl_tri=img_stack_scal_tri,
                              chrds=img_stack_chord,
                              pslices=img_stack_pieslice,
                              rnd_rects=img_stack_rnd_rects,
                              circls=img_stack_circl
                              )
        
    inlet_vel = [10.0, 0.0]
    solve(inlet_vel)

    sim_time = 100
    interpolate(prim_geom, sim_time, domsize, padding)

    
    # creating Signed Distance Field and Flow Region Channel out of generated geometry
    sdf_primitives = create_SDF(prim_geom, padding)
    frc_primitives = create_flowRegionChannel(prim_geom, domsize, padding)

    # creating an array that contains the x and y components of the stream
    #x_comp = np.full((int(domsize[1]/2), domsize[0]), 9.848) # cos(10°)
    #y_comp = np.full((int(domsize[1]/2), domsize[0]), 1.736) # sin(10°)     
    x_comp = np.full((int((imgsize[1]/2)), imgsize[0]), inlet_vel[0]) # cos(10°)
    y_comp = np.full((int((imgsize[1]/2)), imgsize[0]), inlet_vel[1]) # sin(10°) 

    vel_info = np.vstack((x_comp,y_comp))
    vel_info = vel_info[np.newaxis,:,:]
    vel_info = np.repeat(vel_info,prim_geom.shape[0],axis=0)
    print(vel_info.shape)
    print(sdf_primitives.shape)
    print(frc_primitives.shape)


    # merging and reshaping channels to meet input criteria of CNN
    toPickle = list(zip(sdf_primitives, frc_primitives, vel_info))
    toPickle = np.asarray(toPickle)

    #toPickle = np.stack((sdf_primitives, frc_primitives, vel_info), axis = 3)
    #toPickle = toPickle.reshape((-1, 3, imgsize[0], imgsize[1]))

    
    with open('primitives.pkl', 'wb') as f:
        # use pickle to serialize and save the NumPy array
        pickle.dump(prim_geom, f)
    
    
    # creating pickle output file
    pickle.dump(toPickle, open("test_input_x.pkl","wb"))    

    print('Well done!')
