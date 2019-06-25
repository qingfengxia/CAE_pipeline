from __future__ import print_function, division
import math
import os.path
import numpy as np

from dolfin import *
from mshr import *

print(dolfin.dolfin_version())
ver = dolfin.dolfin_version().split('.')
if int(ver[0]) <= 2017 and int(ver[1])<2:
    using_VTK = True
else:
    using_VTK = False

mesh_file = 'test.xml'  # salome mesh -> gmsh ->  
def plot_mesh(filename):
    assert  filename[-4:] == ".xml"
    filename_base = filename[:-4]
    mesh = Mesh(filename)
    plot(mesh)

    subdomain_file = filename_base + "_physical_region.xml"
    if os.path.exists(subdomain_file):
        subdomains = MeshFunction("size_t", mesh, subdomain_file)
        plot(subdomains)  # matplotlib will overlay the previous figure

    bmeshfile =filename_base + "_facet_region.xml"
    if os.path.exists(bmeshfile):
        boundaries = MeshFunction("size_t", mesh, bmeshfile)
        plot(boundaries)

plot_mesh(mesh_file)
#meshio-convert does not convert group
#mf = XDMFFile(mpi_comm_world(), 'test.xdmf')
#test_mesh = mf.read()

if using_VTK:
    interactive()
else:
    import matplotlib.pyplot as plt
    plt.show()


def convert_to_hdf5_mesh_file(filename):
    assert  filename[-4:] == ".xml"
    filename_base = filename[:-4]
    mesh = Mesh(filename)
    hdf = HDF5File(mesh.mpi_comm(), filename_base + ".h5", "w")
    hdf.write(mesh, "/mesh")
    subdomain_file = filename_base + "_physical_region.xml"
    if os.path.exists(subdomain_file):
        subdomains = MeshFunction("size_t", mesh, subdomain_file)
        hdf.write(subdomains, "/subdomains")
    bmeshfile =filename_base + "_facet_region.xml"
    if os.path.exists(bmeshfile):
        boundaries = MeshFunction("size_t", mesh, bmeshfile)
    else:
        boundaries = mark_boundary_for_subdomain(mesh, subdomains)
    hdf.write(boundaries, "/boundaries")