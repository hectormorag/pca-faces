# PCA On Face Models
User interface to implement pca on a face model allowing the user to change texture and 3D geometry. 

This code offer as GUI that implements a visualization of a new 3D model, based on a previous model, after processing the PCA (new texture and new geometry). You can find on PCA_faces.py: the PCA for the texture, the PCA for the geometry, a pair of sliders that are able to change the weights of the 2 PCAs, that dynamically change and create a new 3D model and a save function to save new 3D models by clicking on a button.

Run the project using the code below:
```
python PCA_faces.py
```

In case of any error appearing consider that you have to install other libraries, try the following if necessary:
```
pip install imageio
pip install pygame
pip install pyOpenGL pyOpenGL-accelerate
pip install Pillow
pip install numpy
pip install scipy
```

In order to test the code you can load model1.obj and click process. The GUI will display the options to change the face and create a new 3D model. As shown in the following image. 

![alt text](https://github.com/hectormorag/pca-faces/blob/main/images/gui.png)


