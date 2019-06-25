#!/bin/sh

# this script must be run in terminal, source openfoam bashrc
# change geometry in parameter py file
# run FreeCAD_build_geometry.py if you build geometry and export CAD file using FreeCAD

# here abs path to salome and meshing script must be used! adapt path into your own
#/opt/SALOME-8.5.0-UB16.04-SRC/salome -t  /media/sf_OneDrive/gitrepo/seal_design/salome_mesh_seal.py

MESH=labyrinth_seal_2D_1
# assuming gmsh4 is on your search path, I rename v4 as gmsh4 as I have other version 
gmsh4 -format msh2 -o /media/sf_OneDrive/cases/sealmesh/${MESH}.msh -save ${MESH}.med

FOAM_DIR=/media/sf_OneDrive/cases/sealmesh/
if [ ! -d $FOAM_DIR ]; then
    echo '$FOAM_DIR' folder does not exist!
    #copy a tutoral case into it
    exit -1
fi
# copy a openfoam tutorial case into somewhere, and delete the mesh folder
# 
# gmshToFoam need a case file structure to work
cd $(FOAM_DIR)
# assuming you have source openfoam bashrc into your ~/.bashrc
gmshToFoam ${MESH}.msh
foamMeshToFluent
mv  fluentInterface/sealmesh.msh  ../fluentCFD/${MESH}.msh

# in Ansys workbench, you can `replace mesh` in GUI to reuse the previous case setup
# for other solver, it may be possible to run the solver without launch GUI