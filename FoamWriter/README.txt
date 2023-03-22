tutorial copied from the OpenFOAM/incompressible/simpleFoam/2Dairfoil foler

good instructions from: https://www.youtube.com/watch?v=aIvDtyAYnI8

---------------------------------------------------------------------------
1. get mesh from pygmsh and copy into parent folder
!!! 2D mesh did not work for me, I created a 3D mesh with layer thickness of one

2. (temporary) copy transport and turbulance properties from constant folder into parent 
   folder and delete constant folder afterwards

3. in ubuntu terminal: change directory to parent folder

4. run "gmshToFoam NAME OF FILE" and hope for the best

5. check the mesh with : "checkMesh" command

6. change created boundary file in automatically created constant/polyMesh folder
   - type of frontAndBack should be: empty
   - type of outlet should be: patch
   - type of inlet should be: patch
   - type of prmitive should be: wall
   - type of defaultFaces: should be wall
   save boundary

7. check file "U" in "0" folder 
   - frontAndBack type: empty
   - outlet type: zeroGradient
   - inlet type: fixedValue
     inlet value: uniform(x,y,z komponents of stream velocity)
   - primitive type: noSlip
   - defaultFaces type: noSlip

8. check file "p" in "0" folder 
   - frontAndBack type: empty
   - outlet type: fixedValue;
     outlet value: uniform 0
   - inlet type: zeroGradient
   - primitive type: zeroGradient
   - defaultFaces type: zeroGradient

9. check file "nuTilda" in "0" folder 
   - frontAndBack type: empty
   - outlet type: zeroGradient
   - inlet type: fixedValue 
     inlet type: uniform 0.000148
   - primitive type: fixedValue 
     primitive type: uniform 0
   - defaultFaces type: fixedValue 
     defaultFaces type: uniform 0.000148

10. check file "nut" in "0" folder 
   - frontAndBack type: empty
   - outlet type: zeroGradient
   - inlet type: fixedValue 
     inlet type: uniform 0.000148
   - primitive type: nutUSpaldingWallFunction
     primitive type: uniform 0
   - defaultFaces type: nutUSpaldingWallFunction
     defaultFaces type: uniform 0

11. run "renumberMesh -overwrite" for more efficiency during solving

12. copy transport and turbulance properties back to constant folder

13. run simulation by typing "simpleFoam" in ubuntu terminal