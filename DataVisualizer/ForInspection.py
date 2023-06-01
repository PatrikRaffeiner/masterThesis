import pickle
import matplotlib.pyplot as plt
import numpy as np
from math import ceil

y = pickle.load(open("y_data2653_172x79.pkl","rb"))
x = pickle.load(open("x_data2653_172x79.pkl","rb"))
#y = y[:,:,:]
#x = x[:,:,:]

print(y.shape)
print(x.shape)
'''
batch_size = 10
batches = np.array_split(y, len(y) / batch_size)

plt.imshow(y[0,0,:,:].T)
plt.show()

counter = 0
for batch in batches:
    for y_i, i in zip(batch, range(1,batch_size+1)):
        plt.title("primitive number: " + str(counter-1))
        plt.subplot(2,5,i)
        plt.imshow(y_i[0].T)
        
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        counter += 1
    plt.show()
'''
    


elements_to_delete = [8,14,23,73,125,166,172,189,197,245,254,291,407,410,420,451,525,531,607,644,673,700,704,728,744,843,886,917,
                      1057,1065,1081,1106,1110,1160,1179,1192,1331,1403,1439,1561,1577,1601,1674,1777,1905,1914,1937,2014,2041,
                      2084,2107,2131,2153,2164,2197,2203,2205,2209,2283,2287,2316,2328,2393,2402,2445,2453,2466,2608]

new_x = np.delete(x,elements_to_delete, axis = 0)
new_y = np.delete(y,elements_to_delete, axis = 0)

print(new_x.shape)
print(new_y.shape)

pickle.dump(new_x, open("./x_data2585_172x79.pkl","wb")) 
pickle.dump(new_y, open("./y_data2585_172x79.pkl","wb")) 
