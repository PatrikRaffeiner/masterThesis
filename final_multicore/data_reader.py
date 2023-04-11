import pickle
import numpy as np
import matplotlib.pyplot as plt


x = pickle.load(open("./x_data.pkl", "rb"))
y = pickle.load(open("./y_data.pkl", "rb"))

print("x: " + str(x.shape))
print("y: " + str(y.shape))

x1 = x[:,0,:]
x2 = x[:,1,:]
x3 = x[:,2,:]

x = np.stack((x1, x2, x3))

print("x: " + str(x.shape))

plt.subplot(1,3,1)
plt.imshow(y[0])
plt.subplot(1,3,2)
plt.imshow(y[1])
plt.subplot(1,3,3)
plt.imshow(y[2])

plt.show()