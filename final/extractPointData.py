# trace generated using paraview version 5.11.0-RC1
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 11

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'OpenFOAMReader'
ellipse1msh = OpenFOAMReader(registrationName='ellipse1.msh', FileName='\\\\wsl$\\Ubuntu\\home\\patrik_raffeiner\\MasterThesis\\variousTesting\\FoamWriter\\ellipse1\\ellipse1.msh')
ellipse1msh.MeshRegions = ['internalMesh']
ellipse1msh.CellArrays = ['U', 'div(phi)', 'momentError', 'nuTilda', 'nut', 'p']

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

UpdatePipeline(time=100.0, proxy=ellipse1msh)

# create a new 'PassArrays'
passArrays1 = PassArrays(registrationName='PassArrays1', Input=ellipse1msh)
passArrays1.PointDataArrays = ['U', 'div(phi)', 'momentError', 'nuTilda', 'nut', 'p']
passArrays1.CellDataArrays = ['U', 'div(phi)', 'momentError', 'nuTilda', 'nut', 'p']
passArrays1.FieldDataArrays = ['CasePath']

# Properties modified on passArrays1
passArrays1.PointDataArrays = ['U', 'p']
passArrays1.CellDataArrays = []
passArrays1.FieldDataArrays = []

UpdatePipeline(time=100.0, proxy=passArrays1)

# save data
SaveData('//wsl$/Ubuntu/home/patrik_raffeiner/MasterThesis/variousTesting/FoamWriter/ellipse1/pntData.csv', proxy=passArrays1, PointDataArrays=['U', 'p'],
    FieldDataArrays=['CasePath'])