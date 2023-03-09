# This script and the dedicated subscript is to generate 2D primitives
# of various shape and position, create an unstructured mesh to serve as an input file for OpenFOAM,
# and create a Signed Distance Field to serve as an input file for the DeepCFD neuronal network

# Owned and developed by Patrik Raffeiner
# Developed in the course of a master thesis at the Management Center Innsbruck

from functions import *
import pickle
#from graham_scan_algorithm import sort_coordinates
#from region_growing import *
#from draw_edge import *
#from NNsort import *


if __name__ == '__main__':
    # setting size of domain for all primitives
    domsize = (1920,1024)  # row-major order
    domcenter = (int(domsize[0] / 2), int(domsize[1] / 2))

    # generating ellipses
    ellipses_geom, img_stack_ellipses = create_primitive_stack("ellipse", domsize, domcenter, height_div=2,
                                                               width_div=2, angle_div=2)

    edge_list, edge_img = edge_detection(img_stack_ellipses[0:1], domsize)
 

    ordered_edge_list = region_growing(edge_img)


    meshing(ordered_edge_list, domsize)
    

    '''
    # creating Signed Distance Field and Flow Region Channel out of generated geometry
    sdf_ellipses = create_SDF(ellipses_geom)
    frc_ellipses = create_flowRegionChannel(ellipses_geom, domsize)


    # generating rectangles
    rectangles_geom, img_stack_rectangles = create_primitive_stack("rectangle", domsize, domcenter, height_div=6,
                                                                   width_div=3, angle_div=3)

    sdf_rectangles = create_SDF(rectangles_geom)
    frc_rectangles = create_flowRegionChannel(rectangles_geom, domsize)
    wall_sdf = create_wallSDF(domsize, rectangles_geom)

    # merging and reshaping channels to meet input criteria of CNN
    toPickle = np.stack([sdf_rectangles, frc_rectangles, wall_sdf], axis=3)
    toPickle = toPickle.reshape((54, 3, domsize[0], domsize[1]))

    plot_np_arrays(wall_sdf,"wall sdf")
    plot_np_arrays(frc_rectangles,"wall sdf")
    plot_np_array(sdf_rectangles,"wall sdf")
    plot_np_arrays(frc_ellipses, "wall sdf")
    plot_np_arrays(sdf_ellipses, "wall sdf")

    # creating pickle output file
    #pickle.dump(toPickle, open("../DeepCFD/DeepCFD_input.pkl","wb"))
    pickle.dump(toPickle, open("DeepCFD_input.pkl","wb"))

    '''

    print('Well done!')
