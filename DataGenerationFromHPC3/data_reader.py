import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import shutil

# set solutions directory
solutions_dir = "./solutions/"

# get list of all solutions in directory
solutions = os.listdir(solutions_dir)

# create lists for data collection
x = []
y = []

# traverse through all solution folders
for solution in solutions:
    
    try:
        # collect x and y data 
        x_i = pickle.load(open(solutions_dir + solution + "/x_data.pkl", "rb"))
        y_i = pickle.load(open(solutions_dir + solution + "/y_data.pkl", "rb"))
        
        x.append(x_i)
        y.append(y_i)

    except Exception as ex:
       	print(ex)
        print(str(solution) + " does not contain a datapoint. Directory will be removed.")
                
        # Remove the directory and its contents
        shutil.rmtree(solutions_dir + solution)

    

    

    
'''    plt.title("y data")
    plt.subplot(1,3,1)
    plt.imshow(y_i[0])
    plt.subplot(1,3,2)
    plt.imshow(y_i[1])
    plt.subplot(1,3,3)
    plt.imshow(y_i[2])
    plt.show()

    plt.title("x data")
    plt.subplot(1,3,1)
    plt.imshow(x_i[0])
    plt.subplot(1,3,2)
    plt.imshow(x_i[1])
    plt.subplot(1,3,3)
    plt.imshow(x_i[2])
    plt.show()'''



x = np.asarray(x)
y = np.asarray(y)

print("x: " + str(x.shape))
print("y: " + str(y.shape))

pickle.dump(x, open("./x_data172x79.pkl","wb")) 
pickle.dump(y, open("./y_data172x79.pkl","wb")) 
