# Simulation and data generation of the NACA0012 airfoil

This is a derived version of the primitive generation pipeline to simulate flow around the NACA0012 airfoil 
in the same way as the primitive generator processes the primitives. The only difference is that the primitive
generator takes the image of the primitive's geometry as a basis for the process whole (geometry, meshing, creation of SDF & FRC,
interpolation, vizualization), whereas here, the geometry is manually implemented through:

A) Points on a rectangular grid with the size of 172x79. This mimics the geometry that is used in a "normal" process 
when computing the primitives. Due to the low resolution of the grid and the method of expressing the polygon chain of the airfoil
the outcome of the geometry is rather coarse.

B) Points with no fixed grid, directly from the NACA dat file. This method is utilized to create a smooth geometry of the airfoil.


The outcome of the two different methods show the influence of coarse geometry with respect to the low resolution of the images




