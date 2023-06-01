from primgen_functions import *
#from pebble import concurrent
#from concurrent.futures import TimeoutError

import multiprocessing
import itertools
from multiprocessing import Pool
import os
import shutil


if __name__ == '__main__':

    # setting size of domain for all primitives
  imgsize = (172, 79)      # row-major order
  imgcenter = (int(imgsize[0] / 2), int(imgsize[1] / 2))

  # defining pixel widths, heights and angles of the primitives
  primWidths = [15,20,24,29,33,37,47,55,42]
  primHeights = [12,16,21,26,30,40,45,53,35]
  primAngles = [0,20,80,110,170,270, 53, 140]

  # defining diameters for circles
  circleDiameters = [8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60]

  # start and stop position of the slice (25 to 160 is functionally adequate)
  pieSlices = [[25,50,70,100],
              [100,160,90,150]]
  
  # start and stop position of the cord (in degree)
  chrdSlices = [[100,30,90,140],
                [220,120,130,290]]
  

  # wrapping the parameters into a single list 
  # this is needed because the unordered imap method (multiprocessing) 
  # can only handle functions with one argument --> parameterList 
  circle_parameter_list = list(itertools.product(["circle"], circleDiameters , [imgsize], [imgcenter]))
  rect_parameter_list = list(itertools.product(["rectangle"], primWidths, primHeights, primAngles, [imgsize], [imgcenter]))
  isoTri_parameter_list = list(itertools.product(["iso_triangle"], primWidths, primHeights, primAngles, [imgsize], [imgcenter]))
  scalTri_parameter_list = list(itertools.product(["scalene_triangle"], primWidths, primHeights, primAngles, [imgsize], [imgcenter]))
  ellipse_parameter_list = list(itertools.product(["ellipse"], primWidths, primHeights, primAngles, [imgsize], [imgcenter]))
  rndRect_parameter_list = list(itertools.product(["rounded_rectangle"], primWidths, primHeights, primAngles, [imgsize], [imgcenter]))
  pie_parameter_list = list(itertools.product(["pieslice"], primWidths, primHeights, primAngles, pieSlices, [imgsize], [imgcenter]))
  chord_parameter_list = list(itertools.product(["chord"], primWidths, primHeights, primAngles, chrdSlices, [imgsize], [imgcenter]))
  
  '''
  # creating a folder to store meshes
  if not os.path.exists("./meshes"):
    os.makedirs("./meshes")

  else:
    # Remove the directory and its contents
    shutil.rmtree('./meshes')
    os.makedirs("./meshes")

  # creating a folder to store solutions
    if not os.path.exists("./solutions"):
      os.makedirs("./solutions")

    else:
      # Remove the directory and its contents
      shutil.rmtree('./solutions')
      os.makedirs("./solutions")
   '''

  # using multiprocessing for parallel processing of the procedure
  with Pool(processes = multiprocessing.cpu_count() -1) as pool:
    
    # kick off the parallel processing 
    # circles
    #for prim in pool.imap_unordered(makePrim, circle_parameter_list):
    #  pass


    # rectangles
    #for prim in pool.imap_unordered(makePrim, rect_parameter_list):
    #  pass
   

    # iso triangles
    #for prim in pool.imap_unordered(makePrim, isoTri_parameter_list):
    #  pass
    
    # scalene triangles
    #for prim in pool.imap_unordered(makePrim, scalTri_parameter_list):
    #  pass

    # ellipses
    #for prim in pool.imap_unordered(makePrim, ellipse_parameter_list):
    #  pass 
    
    # rounded rectangles
    #for prim in pool.imap_unordered(makePrim, rndRect_parameter_list):
    #  pass

    # pieslices
    #for prim in pool.imap_unordered(makePrim, pie_parameter_list):
    #  pass
    
    # chords
    for prim in pool.imap_unordered(makePrim, chord_parameter_list):
      pass

