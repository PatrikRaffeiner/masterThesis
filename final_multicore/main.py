from primgen_functions import *

import multiprocessing
import itertools
from multiprocessing import Pool
import os
import shutil





if __name__ == '__main__':

  # defining pixel widths, heights and angles of the primitives
  primWidths = [100,40,400]
  primHeights = [100]
  primAngles = [10]

  # start and stop position of the cord (in degree)
  primChords = [[100, 200],
                [220, 10]]
  
  # start and stop position of the slice (25 to 160 is functionally adequate)
  primPies = [[25,50],
              [100,160]]


  # setting size of domain for all primitives
  imgsize = (1920, 1024)      # row-major order
  padding = 20                # padding to be removed along image edge (cubic interpolation) 
  domsize = (imgsize[0] + 2*padding, imgsize[1] + 2*padding)
  domcenter = (int(domsize[0] / 2), int(domsize[1] / 2))
      

  # wrapping the parameters into a single list 
  # this is needed because the unordered imap method (multiprocessing) 
  # can only handle functions with one argument --> parameterList 
  prim_parameter_list = list(itertools.product(["pieslice"], primWidths, primHeights, primAngles, primPies, [domsize], [domcenter], [padding]))

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
  


  # using multiprocessing for parallel processing of the procedure
  with Pool(processes=multiprocessing.cpu_count() -1) as pool:
    
    # kick off the parallel processing by generating the primitive images
    for prim in pool.imap_unordered(makePrim, prim_parameter_list):
      pass
      
      # sort out bad primitives 
      #if prim != False:

        #prim.show()

        #np_prim = np.asarray(prim)
        #frc = create_flowRegionChannel(np_prim, padding)
        #sdf = create_SDF(np_prim, padding)



# TODO: try the built-in pygmsh method to get unfolded polygon train 





