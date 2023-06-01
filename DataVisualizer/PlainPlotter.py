import pickle
import matplotlib.pyplot as plt
import numpy as np


y = pickle.load(open("y_data.pkl","rb"))
x = pickle.load(open("x_data.pkl","rb"))
y = y[:,:,:]
x = x[:,:,:]

print(y.shape)
print(x.shape)

edgeCoords = pickle.load(open("edgeCoords.pkl","rb"))

print(edgeCoords.shape)
print(edgeCoords[0][0])

edgeimg = np.zeros([172,79])
for px in edgeCoords:
    edgeimg[int(px[0]), int(px[1])] =1

plt.imshow(edgeimg.T)
plt.show()



plt.subplot(2,1,1)
plt.imshow(y[0,:,:].T, cmap="turbo")
plt.title('y-Data', fontsize=18)
plt.gca().invert_yaxis()
plt.colorbar(orientation='horizontal')
plt.subplot(2,1,2)
plt.imshow(x[1,:,:].T, cmap="turbo")
plt.title('x-Data', fontsize=18)
plt.gca().invert_yaxis()
plt.colorbar(orientation='horizontal')
plt.show()

'''for y_i, i in zip(y,range(0,y.shape[0])):
    plt.suptitle("primitive number: " + str(i))
    plt.subplot(2,2,1)
    plt.imshow(y_i[0].T)
    plt.subplot(2,2,2)
    plt.imshow(y_i[1].T)
    plt.subplot(2,2,3)
    plt.imshow(y_i[2].T)
    
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()
'''

'''elements_to_delete = [5,52,125,135,168,175,210,250,266,352,387,654,765]

new_x = np.delete(x,elements_to_delete, axis = 0)
new_y = np.delete(y,elements_to_delete, axis = 0)

print(new_x.shape)
print(new_y.shape)

pickle.dump(new_x, open("./x_data763_172x79.pkl","wb")) 
pickle.dump(new_y, open("./y_data763_172x79.pkl","wb")) 
'''