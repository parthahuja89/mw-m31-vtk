# MW-M31-VTK
## About Project
This is a visualization of a galaxy in the [IllustrisTNG project](https://www.tng-project.org/data/milkyway+andromeda/). The code for this project uses VTK and Python 3. The original files (342447.hdf5) were converted into an unstructured VTK grid using h5py. 
## Data Download 
You can access the data on the following [Link](https://drive.google.com/file/d/1uSjKHxVC-VkxUxWCKlUWu4pYgbrWovbk/view?usp=sharing). The file size is around 2GB.
## Execute code 
Replace dir with your directory where you downloaded the data.  <br />
Note: You can also switch to gas-output.vtk for more points <br />
` python vis-gui.py -a [dir/data/gas-output-mini.vtk] -c [dir/data/ctfs/ctf.txt] `
## Results 
Some of the images from the results: <br />
Density Image 1: <br />
![Density-1](images/density-1.png)
Density Image 2: <br />
![Density-2](images/density-2.png)
Internal Energy Image 1: <br />
![Internal-1](images/internal-1.png)
Internal Energy Image 2: <br />
![Internal-2](images/internal-2.png)
Velocity Image 1: <br />
![Velocity-1](images/velocity-1.png)
Velocity Image 2: <br />
![Velocity-2](images/velocity-2.png)
Magnetic Field Image 1: <br />
![Magnetic-1](images/mag-1.png)
Magnetic Field Image 2: <br />
![Magnetic-2](images/mag-2.png)