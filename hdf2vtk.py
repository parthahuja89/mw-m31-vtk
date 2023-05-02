import vtk
import h5py
import numpy as np
import argparse
# Define the file path and name
parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, required=True, help='Path to the HDF5 file')
args = parser.parse_args()
PARENT_SIZE = 5337612
SAMPLE_SIZE = 25000

x_min, x_max = 25015.3, 25071.4
y_min, y_max = 5807.92, 5843.36
z_min, z_max = 34159.5, 34224.9

with h5py.File(args.f, 'r') as f:
    # print all keys
    print("Keys: %s" % f.keys())

    # access 'PartType0' group
    part_type_0 = f['PartType0']
    # print the keys of the 'PartType0' group
    print("Keys in PartType0 group: %s" % part_type_0.keys())

    # extract coordinates, density, and internal energy of particles
    coordinates = part_type_0['Coordinates']
    density = part_type_0['Density']
    internal_energy = part_type_0['InternalEnergy']
    velocity = part_type_0['Velocities']
    magnetic_field = part_type_0['MagneticField']

    # select indices of particles within the boundary box
    x_mask = (coordinates[:, 0] >= x_min) & (coordinates[:, 0] < x_max)
    y_mask = (coordinates[:, 1] >= y_min) & (coordinates[:, 1] < y_max)
    z_mask = (coordinates[:, 2] >= z_min) & (coordinates[:, 2] < z_max)
    indices = np.where(x_mask & y_mask & z_mask)[0]
    print('Number of particles within the boundary box: %d' % len(indices))
    # randomly sample SAMPLE_SIZE particles from selected indices
    indices = np.random.choice(indices, size=SAMPLE_SIZE, replace=False)
    indices.sort()

    # extract selected particles' coordinates, density, and internal energy
    coordinates = coordinates[indices]
    density = density[indices]
    internal_energy = internal_energy[indices]
    velocity = velocity[indices]
    magnetic_field = magnetic_field[indices]
    
# print(np.array2string(density, max_line_width=np.inf, threshold=np.inf))
# Create a vtkUnstructuredGrid object
grid = vtk.vtkUnstructuredGrid()

# Create a vtkPoints object and add the particle coordinates to it
points = vtk.vtkPoints()
for i in range(SAMPLE_SIZE):
    points.InsertNextPoint(coordinates[i])
grid.SetPoints(points)

# Create a vtkDoubleArray object for density and add it to the grid
density_array = vtk.vtkDoubleArray()
density_array.SetName('Density')
density_array.SetNumberOfComponents(1)
for i in range(SAMPLE_SIZE):
    density_array.InsertNextTuple1(density[i])
grid.GetPointData().AddArray(density_array)

# Create a vtkDoubleArray object for internal energy and add it to the grid
internal_energy_array = vtk.vtkDoubleArray()
internal_energy_array.SetName('InternalEnergy')
internal_energy_array.SetNumberOfComponents(1)
for i in range(SAMPLE_SIZE):
    internal_energy_array.InsertNextTuple1(internal_energy[i])
grid.GetPointData().AddArray(internal_energy_array)

# Create a vtkDoubleArray object for velocity and add it to the grid
velocity_array = vtk.vtkDoubleArray()
velocity_array.SetName('Velocity')
velocity_array.SetNumberOfComponents(3)
for i in range(SAMPLE_SIZE):
    velocity_array.InsertNextTuple3(velocity[i][0], velocity[i][1], velocity[i][2])
grid.GetPointData().AddArray(velocity_array)

# Create a vtkDoubleArray object for magnetic field and add it to the grid
magnetic_field_array = vtk.vtkDoubleArray()
magnetic_field_array.SetName('MagneticField')
magnetic_field_array.SetNumberOfComponents(3)
for i in range(SAMPLE_SIZE):
    magnetic_field_array.InsertNextTuple3(magnetic_field[i][0], magnetic_field[i][1], magnetic_field[i][2])
grid.GetPointData().AddArray(magnetic_field_array)

# Write the vtkUnstructuredGrid object to a VTK file
writer = vtk.vtkUnstructuredGridWriter()
writer.SetFileName('gas-output-mini.vtk')
writer.SetInputData(grid)
writer.Write()



