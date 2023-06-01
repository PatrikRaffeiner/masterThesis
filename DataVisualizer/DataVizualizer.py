import pickle
import matplotlib.pyplot as plt
import numpy as np


y_NACA_smooth = pickle.load(open("y_smooth.pkl","rb"))
x_NACA_smooth = pickle.load(open("x_smooth.pkl","rb"))
y_NACA_smooth = y_NACA_smooth[0]
x_NACA_smooth = x_NACA_smooth[0]
y_NACA_pixelated = pickle.load(open("y_pixelated.pkl","rb"))
x_NACA_pixelated = pickle.load(open("x_pixelated.pkl","rb"))
print(y_NACA_smooth.shape)
print(y_NACA_pixelated.shape)

error = y_NACA_smooth - y_NACA_pixelated


plt.subplot(2,2,1)
plt.imshow(y_NACA_smooth[2,:,:].T, cmap="turbo")
plt.title('Smooth geometry', fontsize=18)
plt.gca().invert_yaxis()
plt.colorbar(orientation='horizontal')
plt.subplot(2,2,2)
plt.imshow(y_NACA_pixelated[2,:,:].T, cmap="turbo")
plt.title('Pixelated geometry', fontsize=18)
plt.gca().invert_yaxis()
plt.colorbar(orientation='horizontal')
plt.subplot(2,2,3)
plt.imshow(error[2,:,:].T, cmap="turbo")
plt.title('Error', fontsize=18)
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