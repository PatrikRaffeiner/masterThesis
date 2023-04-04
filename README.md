# masterThesis
Accompanying code for the master thesis written at the MCI in the study program Medichal Technologies.
The content below is completely automated and written 100% in python. The main file can be found under masterThesis_main.

Content:
- Generation of primitives at various positions and orientations via PIL 

- Generation of data input "dataX" to match the 1st input of the DeepCFD network:
	+ Calculation of Signed Distance Fields (SDF)  via snowy
	+ Calculation of Flow Region Channels (FRC) 
	+ Additional info of velocity-input components

- Meshing of primitives and definition of boundary conditions via pygmsh/gmsh

- Fluid simulation of generated primitives + boundary conditions via OpenFOAM

- Interpolation of of Ux, Uy, and p from an unstructured mesh into structured grid with recess of the primitive shape

- Generation of data input "dataY" to match the 2st input of the DeepCFD network:
