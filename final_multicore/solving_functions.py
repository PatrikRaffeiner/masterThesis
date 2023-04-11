import os
import shutil
import subprocess


def solve(mesh_name, inlet_vel):
    # Step1: creating a new folder including the setup and copying the specific mesh
    # Step2: turning the pre-generated mesh from pygmsh into a mesh that can be red by OpenFOAM

    # Set directory where all pre-meshes are located
    mesh_dir = "./meshes"

    # Set the destination path where a simulation-folder is generated for each primitive
    # This folder will include all necessary elements to run the simulation in OpenFOAM
    dest_path = "./solutions/" + mesh_name

    # Copying the simulation-folder and corresponding pre-mesh
    shutil.copytree("./dummyFolder", dest_path)
    shutil.copy(mesh_dir + "/" + mesh_name + ".msh2", dest_path)

    # Define the command to run gmshToFoam
    #  -case specifies the optional work directory
    print(dest_path + "/" + mesh_name + ".msh2")
    command = ["gmshToFoam", "-case", dest_path, dest_path + "/" + mesh_name + ".msh2"]

    # Run gmshToFoam
    # This will turn the pre-mesh into a mesh that can be used as input for OpenFOAM
    # and create the subfolder structure including the boundary files to run the simulation
    subprocess.check_call(command, stdout=subprocess.DEVNULL)

    # Step3: adjust the generated files (boundary, U, p, nuTilda and nu)

      # Open boundary file, located in 'constant' folder, in read mode
    with open(dest_path + "/constant/polyMesh/boundary", "r") as boundary_file:
        # read the content of the file
        boundary_content = boundary_file.readlines()

    # Manipulate the content of the boundary file to the correct types & values
        '''
        # for openFoam v2012
        boundary_content[21] = "\t\ttype \t\t\tempty; \n"       # change frontAndBack from type patch to empty
        boundary_content[42] = "\t\ttype \t\t\twall; \n"        # change primitive from type patch to wall
        boundary_content[49] = "\t\ttype \t\t\twall; \n"        # change defaultFaces from type patch to wall
        '''
    # for openFoam 9
    # change frontAndBack from type patch to empty
    boundary_content[21] = "\t\ttype \t\t\tempty; \n"
    # change primitive from type patch to wall
    boundary_content[42] = "\t\ttype \t\t\twall; \n"
    # change defaultFaces from type patch to wall
    boundary_content[49] = "\t\ttype \t\t\twall; \n"

    # Write changes to boundary file
    with open(dest_path + "/constant/polyMesh/boundary", "w") as boundary_file:
        boundary_file.writelines(boundary_content)
    

#------------------------------------------------------------------------#

    # TODO: adjust nut
    '''
    # open nut file, located in '0' folder, in read mode
    with open("0/nut","r") as nut_file:
        # read the content of the file
        nut_content = nut_file.readlines()

    # manipulate the content of the nut file to the correct types & values
    nut_content[21] = "\t\ttype \t\t\tempty; \n"       # change frontAndBack from type patch to empty

    # write changes to boundary file
    with open("0/nut","w") as nut_file:
        nut_file.writelines(nut_content)

    '''
    # TODO: adjust nuTilda

    # open U file, located in '0' folder, in read mode
    with open(dest_path + "/0/U","r") as U_file:
        # read the content of the file
        U_content = U_file.readlines()

    # manipulate the content of the U file to the correct inlet values
    U_content[35] = "\t\tvalue \t\t\tuniform (" + str(inlet_vel[0]) + " " + str(inlet_vel[1]) + " 0.0); \n"    # change the x,y,z components accordingly        

    # write changes to boundary file
    with open(dest_path + "/0/U","w") as U_file:
        U_file.writelines(U_content)



    ### Step3: copy the transport and turbulence properties to the generated constant folder

    # Source path of the files to be copied
    src_file_path = 'toPaste'

    # Destination path where the files will be copied
    dest_file_path = dest_path +'/constant'

    # Copy the files to constant folder
    os.system('cp {} {}'.format(src_file_path+'/transportProperties', dest_file_path+'/transportProperties'))
    #os.system('cp {} {}'.format(src_file_path+'/turbulenceProperties', dest_file_path+'/turbulenceProperties'))
    os.system('cp {} {}'.format(src_file_path+'/momentumTransport', dest_file_path+'/momentumTransport'))

    ### Step4: run "renumberMesh" for more efficiency during solving

    # Define the command to run renumberMesh
    #  -case specifies the optional work directory
        
    # does not work on mehcp3
    #command = ["renumberMesh", "-overwrite", "-case", dest_path] 

    # Run renumberMesh
    #subprocess.check_call(command)


    ### Step5: Run the OpenFOAM simulation

    # Define the command to run renumberMesh
    #  -case specifies the optional work directory
    command = ["simpleFoam", "-case", dest_path] 

    # Run renumberMesh
    subprocess.check_call(command, stdout=subprocess.DEVNULL)    
