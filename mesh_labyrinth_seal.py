# -*- coding: utf-8 -*-
from __future__ import print_function, division


'''
# to find parameter_salome in the current folder, if caller script is not in this folder
try:
    os.chdir('/media/sf_OneDrive/gitrepo/seal_design')  # change to working dir
except:
    print('First of all, os.chdir to the folder where salome_parameter.py is located')
    sys.exit()
    #os.chdir('/media/OneDrive/Fenics/metal_cut/')
'''

######################################
#/opt/SALOME-8.5.0-UB16.04-SRC/runSalome -t -b /myScript
#can not make a symbolic link to this salome
#/opt/SALOME-9.3.0-UB16.04-SRC/salome -t -b /myScript
## the sequence of gmsh options is important, your gmsh maybe called gmsh, gmsh version 4 is required
#gmsh4 -format msh2   -o metal_cut.msh -save Mesh_1.med
#dolfin-convert metal_cut.msh metal_cut.xml
##########################################

from math import sin, cos, tan, pi, atan2

from seal_parameter import *  # restart salome if any change in this parameter file
# for quick testing, copy parameter.py content here


###
### This file is generated automatically by SALOME v8.5.0 with dump python functionality
###
import os
import sys
import salome

salome.salome_init()
theStudy = salome.myStudy

import salome_notebook
notebook = salome_notebook.NoteBook(theStudy)
# rotate those points or rotate the face
###
### GEOM component
###


import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS

#============================
try:
    geompy = geomBuilder.New(theStudy)
except:
    geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
OZ_minus = geompy.MakeVectorDXDYDZ(0, 0, -1)

geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )


def near(pa, pb, rtol = 1e-3):
    if isinstance(pa, (int, float)) and isinstance(pb, (int, float)):
        if max([math.fabs(pa), math.fabs(pb)]) < 1e-6:  # including both are zero
            return math.fabs(pa-pb) / 1e-6 < rtol
        else:
            return math.fabs(pa-pb) / max([math.fabs(pa), math.fabs(pb)]) < rtol
    else:
        A = geompy.PointCoordinates(pa)
        B = geompy.PointCoordinates(pb)
        dist2 = sum([(A[i]-B[i])*(A[i]-B[i]) for i in range(3)])
        return dist2 < rtol*0.001

def edge_length(edge):
    if len(geompy.ExtractShapes(edge, geompy.ShapeType["VERTEX"], True)) !=2:
        print(edge, "edge is not a line with two points")
        return None
    else:
        [pa, pb] = geompy.ExtractShapes(edge, geompy.ShapeType["VERTEX"], True)
        A = geompy.PointCoordinates(pa)
        B = geompy.PointCoordinates(pb)
        dist2 = sum([(A[i]-B[i])*(A[i]-B[i]) for i in range(3)])
        return dist2**0.5

def get_shape_list_by_center_condition(geom, cond, shape_type = "EDGE"):
    edgelist = geompy.ExtractShapes(geom, geompy.ShapeType[shape_type], True)
    elist = []
    for i,e in enumerate(edgelist):
        cg = geompy.PointCoordinates(geompy.MakeCDG(e))  #center of gravity, only for solid? return type?
        if cond(cg):  #z-coordinate
            elist.append(e)
            #geompy.addToStudyInFather( geom, e, "Edge_{}".format(i))
            # geompy.getCoordinate(vertex)  # return a 3elm tuple?
    return elist

def add_group_by_condition(geom, cond, shape_type, group_name):
    # can use various property to filter element
    slist = geompy.ExtractShapes(geom, geompy.ShapeType[shape_type], True)
    elist = []
    for i,e in enumerate(slist):
        if cond(e):  #z-coordinate
            elist.append(e)
    shape_group = geompy.CreateGroup(geom, geompy.ShapeType[shape_type])
    geompy.UnionList(shape_group, elist)
    geompy.addToStudyInFather(geom, shape_group, group_name)
    return shape_group

def add_group_by_center_condition(geom, cond, shape_type, group_name):
    sl = get_shape_list_by_center_condition(geom, cond, shape_type = shape_type)
    shape_group = geompy.CreateGroup(geom, geompy.ShapeType[shape_type])
    geompy.UnionList(shape_group, sl)
    geompy.addToStudyInFather(geom, shape_group, group_name)
    return shape_group

def get_edge_list_by_length_condition(geom, cond):
    edgelist = geompy.ExtractShapes(geom, geompy.ShapeType["EDGE"], True)  # True means ?
    elist = []
    for i,e in enumerate(edgelist):
        cg = geompy.PointCoordinates(geompy.MakeCDG(e))  #center of gravity, only for solid? return type?
        l = edge_length(e)
        if l and cond(cg, l):  #z-coordinate
            elist.append(e)
            #geompy.addToStudyInFather( geom, e, "Edge_{}".format(i))
            # geompy.getCoordinate(vertex)  # return a 3elm tuple?
    return elist

if sys.version_info[0]>=3:
    # python 3 has no execfile, but exec() does not give error line number <string>  <module>
    pass

###########################################

seal_points = generate_seal_xy(N_tooth_group)
# turning the points position for different valve opening angle,   +cos(alpha)*r_stator
rotor_points = generate_rotor_xy(N_tooth_group)

wall_vlist = [geompy.MakeVertex(px, py, z0) for (px, py) in seal_points]
rotor_vlist = [geompy.MakeVertex(px, py, z0) for (px, py) in rotor_points]

print(inlet_points)
inlet_vlist = [geompy.MakeVertex(px, py, z0) for (px, py) in inlet_points]
outlet_vlist = [geompy.MakeVertex(px, py, z0) for (px, py) in outlet_points]
#close the loop, relly depends on 
rotor_vlist.insert(0, inlet_vlist[0])
rotor_vlist.append(outlet_vlist[0])
inlet_vlist.append(wall_vlist[0])
outlet_vlist.append(wall_vlist[-1])

# div = geompy.DivideEdgeByPoint( box, edge, [p1, p2], theName="box (edge divided)")
#    Shape is a shape, which contains an edge to be divided;
#    Edge is an edge to be divided (or its ID, if it is = -1, then Shape should be an edge itself);
#    Points is a list of points to be projected to the Edge.

line_inlet_gap = geompy.MakePolyline([rotor_vlist[1], wall_vlist[2]])
line_outlet_gap = geompy.MakePolyline([rotor_vlist[-1], wall_vlist[-1]])


split_tool = []


rotor_profile = geompy.MakePolyline(rotor_vlist)
wall_profile = geompy.MakePolyline(wall_vlist)
inlet_profile = geompy.MakePolyline(inlet_vlist)
outlet_profile = geompy.MakePolyline(outlet_vlist)
geompy.addToStudy(rotor_profile, 'rotor_profile')
geompy.addToStudy(wall_profile, 'wall_profile')
geompy.addToStudy(inlet_profile, 'inlet_profile')
geompy.addToStudy(outlet_profile, 'outlet_profile')

#geompy.MakeRotation(Shape, Axis, angle)

#===============build geomtry=================
Face_1 = geompy.MakeFaceWires([inlet_profile, rotor_profile, outlet_profile, wall_profile], 1)  #
Partition_1 = geompy.MakePartition([Face_1], split_tool, [], [], geompy.ShapeType["FACE"], 0, [], 0)
geompy.addToStudy(Partition_1, 'Partition_1')

if using_3D:
    Extrusion_1 = geompy.MakePrismVecH(Partition_1, OZ, extrusion_thickness)
    geompy.addToStudy( Extrusion_1, 'Extrusion_1' )

    domain = Extrusion_1
    #is there a way to detect whether a point is in solid?
    vlist = geompy.ExtractShapes(domain, geompy.ShapeType["SOLID"], True)
    solid_type = "SOLID"
    boundary_type = "FACE"
else:
    domain = Partition_1
    #is there a way to detect whether a point is in solid?
    vlist = geompy.ExtractShapes(domain, geompy.ShapeType["FACE"], True)
    solid_type = "FACE"
    boundary_type = "EDGE"

# ============ export CAD file ============
#
#geompy.ExportSTEP(domain, geom_filename, GEOM.LU_MILLIMETER)  #length unit

'''
slist = geompy.ExtractShapes(domain, geompy.ShapeType['SOLID'], True)
elist = []
for i,e in enumerate(slist):
    p = geompy.PointCoordinates(geompy.MakeCDG(e))
    A = geompy.BasicProperties(e)[1]
    volume = geompy.BasicProperties(e)[2]
    print(p)
    print(volume)
'''
############## group geomtry for meshing propurse ##########
# ========== solid group ============

#if domain is not split, all_regions has nothing selected, why?
all_regions = add_group_by_center_condition(domain, lambda p: True, solid_type, 'all_regions')
# could be useful in region init
cond_upstream = lambda p: p[0] < seal_min_x
upstream_regions = add_group_by_center_condition(domain, cond_upstream, solid_type, 'upstream_regions')
cond_downstream = lambda p: p[0] > seal_max_x
downstream_regions = add_group_by_center_condition(domain, cond_downstream, solid_type, 'downstream_regions')
cond_seal = lambda p: p[0] < seal_max_x and p[0] < seal_min_x
downstream_regions = add_group_by_center_condition(domain, cond_downstream, solid_type, 'seal_regions')

#########################################################

#Face_rotor_rim = add_group_by_condition(domain, cond_rotor_rim, boundary_type, 'Face_rotor_rim')
#Face_rotor_chamfer = add_group_by_condition(domain, cond_rotor_chamfer, boundary_type, 'Face_rotor_chamfer')
#cond_hole_gap_interface = lambda p: p[0] < rotor_centerline_x + thickness * 0.35 and p[0] > rotor_centerline_x - thickness * 0.35\


# =========== edges =============

short_edge_cond = lambda p, l: math.fabs(l) < small_edge_length_threshold  and math.fabs(p[2]) < 1e-8
long_edge_cond = lambda p, l: math.fabs(l) > long_edge_length_threshold  #  and math.fabs(p[2]) < 1e-8

# independent of 2D or 3D, in same case,  heat thickness is not counted as short edge

velist = get_edge_list_by_length_condition(domain, short_edge_cond)
ShortEdgeGroup = geompy.CreateGroup(domain, geompy.ShapeType["EDGE"])
geompy.UnionList(ShortEdgeGroup, velist)
geompy.addToStudyInFather(domain, ShortEdgeGroup, 'ShortEdgeGroup' )


velist = get_edge_list_by_length_condition(domain, long_edge_cond)
LongEdgeGroup = geompy.CreateGroup(domain, geompy.ShapeType["EDGE"])
geompy.UnionList(LongEdgeGroup, velist)
geompy.addToStudyInFather(domain, LongEdgeGroup, 'LongEdgeGroup' )

if using_3D:
    #cond_vertical = lambda p: math.fabs(p[2] - 0.5*extrusion_thickness) < 1e-5
    vertical_edge_cond = lambda p, l: math.fabs(p[2] - 0.5*extrusion_thickness) < 1e-5  # should automatically filter out cricle edge
    #velist = get_shape_list_by_edge_(domain, cond_vertical)
    velist = get_edge_list_by_length_condition(domain, vertical_edge_cond)
    VerticalEdgeGroup = geompy.CreateGroup(domain, geompy.ShapeType["EDGE"])
    geompy.UnionList(VerticalEdgeGroup, velist)
    geompy.addToStudyInFather(domain, VerticalEdgeGroup, 'VerticalEdgeGroup')

if using_3D:
    on_boundary = lambda p: near(p[2], extrusion_thickness*0.5)  # internal faces also selected, only for quasi-2D cases
else:
    on_boundary = lambda p: True


# ============== boundary =============
_small_dist = 1e-6
cond_inlet = lambda p:  on_boundary(p) and (p[0] < seal_min_x-_small_dist and not near(p[1], rotor_min_y))
cond_outlet = lambda p:  on_boundary(p) and (p[0] > seal_max_x+_small_dist and not near(p[1], rotor_min_y))
                            
def cond_wall(e):
    p = geompy.PointCoordinates(geompy.MakeCDG(e))
    A = geompy.BasicProperties(e)[1]  # length, area, volume
    b1 = on_boundary(p) and p[1]>rotor_min_y+_small_dist  and p[1]<seal_origin[1]+_small_dist \
                            and p[0] > seal_min_x-gap and p[0] < seal_max_x+gap
    b2 = not (near(A, extrusion_thickness*rotor_step_height) or near(p[1], rotor_max_y))
    return b1 and b2

def cond_rotor(e):
    p = geompy.PointCoordinates(geompy.MakeCDG(e))
    A = geompy.BasicProperties(e)[1]  # length, area, volume
    b1 = on_boundary(p) and p[1]< rotor_max_y+1e-6
    b2 = near(A, extrusion_thickness*rotor_step_height)  or near(p[1], rotor_max_y)  or near(p[1], rotor_min_y)
    return b1 and b2

if using_pressure_tapping_hole:
    tap_g = add_group_by_condition(domain, cond_tap_wall, boundary_type, 'tap_wall')

cond_front = lambda p: near(p[2], z0+extrusion_thickness)
front_g = add_group_by_center_condition(domain, cond_front, boundary_type, 'front_g')
cond_back = lambda p: near(p[2], z0)
back_g = add_group_by_center_condition(domain, cond_back, boundary_type, 'back_g')

inlet_g = add_group_by_center_condition(domain, cond_inlet, boundary_type, 'inlet_g')
outlet_g = add_group_by_center_condition(domain, cond_outlet, boundary_type, 'outlet_g')
wall_g = add_group_by_condition(domain, cond_wall, boundary_type, 'wall_g')
rotor_g = add_group_by_condition(domain, cond_rotor, boundary_type, 'rotor_g')

# internal edges are also selected
viscous_layer_g =  geompy.CreateGroup(domain, geompy.ShapeType[boundary_type])   # list of subshape
geompy.UnionIDs(viscous_layer_g, geompy.GetObjectIDs(wall_g))
geompy.UnionIDs(viscous_layer_g, geompy.GetObjectIDs(rotor_g))
geompy.addToStudyInFather(domain, viscous_layer_g, 'viscous_layer_g' )

###################################################
if salome.sg.hasDesktop():
    try:
        salome.sg.updateObjBrowser(True)  # salome v8
    except:
        salome.sg.updateObjBrowser()

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New(theStudy)

Mesh_1 = smesh.Mesh(domain, 'CFD')
Regular_1D = Mesh_1.Segment()
Number_of_Segments_default = Regular_1D.NumberOfSegments(line_segment_nb_default)
# table desity, is kind of viscous layer
Number_of_Segments_default.SetNumberOfSegments( line_segment_nb_default )
Number_of_Segments_default.SetConversionMode( 1 )
Number_of_Segments_default.SetReversedEdges( [] )
Number_of_Segments_default.SetTableFunction( [ 0, 3, 0.2, 1, 0.8, 1, 1, 3 ] )

smesh.SetName(Number_of_Segments_default, 'Number_of_Segments_default')
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')


#####################################
bl_thickness = gap*0.1 # total thickness
bl_numberOfLayers = 3
bl_stretchFactor = 1.5


if using_quad_mesh:
    Quadrangle_2D = Mesh_1.Quadrangle(algo=smeshBuilder.QUADRANGLE)  # or limited to a group: geom=FaceGroupQuadMesh
    mesh2D = Quadrangle_2D
    smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
else:
    MEFISTO_2D = Mesh_1.Triangle(algo=smeshBuilder.MEFISTO)
    smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
    mesh2D = MEFISTO_2D


'''
ViscousLayers.SetTotalThickness( gap*0.1 )
ViscousLayers.SetNumberLayers( 5 )
ViscousLayers.SetStretchFactor( 1.2 )
#ViscousLayers.SetIgnoreFaces( [ 34, 48, 14, 26, 42, 45 ] )
ViscousLayers.SetIgnoreEdges(non_viscous_faces.GetSubShapeIndices())   # geompy.SubShapeAllIDs(shape, type)
mesh.AddHypothesis()
'''

#SegmentAroundVertex_0D = smesh.CreateHypothesis('SegmentAroundVertex_0D')
#status = Mesh_1.AddHypothesis(SegmentAroundVertex_0D,Auto_group_for_Sub_mesh_2)



#=========== submesh ==========

Regular_1D_large= Mesh_1.Segment(geom=LongEdgeGroup)
Number_of_Segments_large = Regular_1D_large.NumberOfSegments(line_segment_nb_large)
status = Mesh_1.AddHypothesis(Number_of_Segments_large, domain)
Sub_mesh_large = Regular_1D_large.GetSubMesh()
smesh.SetName(Number_of_Segments_large, 'Number_of_Segments_large')

if using_3D:
    Regular_1D_3 = Mesh_1.Segment(geom=VerticalEdgeGroup)
    Number_of_Segments_vertical = Regular_1D_3.NumberOfSegments(line_segment_nb_vertical)
    Sub_mesh_vertical = Regular_1D_3.GetSubMesh()
    smesh.SetName(Number_of_Segments_vertical, 'Number_of_Segments_vertical')

if True:
    Regular_1D_small = Mesh_1.Segment(geom=ShortEdgeGroup)
    Number_of_Segments_small = Regular_1D_small.NumberOfSegments(line_segment_nb_small)
    Number_of_Segments_small.SetNumberOfSegments( line_segment_nb_small )
    Number_of_Segments_small.SetConversionMode( 1 )
    Number_of_Segments_small.SetReversedEdges( [] )
    Number_of_Segments_small.SetTableFunction( [ 0, 3, 0.2, 1, 0.8, 1, 1, 3 ] )
    
    Sub_mesh_small = Regular_1D_small.GetSubMesh()
    smesh.SetName(Number_of_Segments_small, 'Number_of_Segments_small')
    smesh.SetName(Sub_mesh_small, 'Sub_mesh_small')
    # added to 0D of short egde, but only one points
    Length_Near_Vertex_1 = Regular_1D_small.LengthNearVertex(gap*0.1, ShortEdgeGroup)
    status = Mesh_1.AddHypothesis(Length_Near_Vertex_1, ShortEdgeGroup)
    smesh.SetName(Length_Near_Vertex_1, 'Length Near Vertex_1')

if using_viscous_layers:
    if using_3D:
        Sub_mesh_face_m = Mesh_1.Triangle(algo=smeshBuilder.NETGEN_2D, geom=back_g)
        
        Max_Element_Area_1 = Sub_mesh_face_m.MaxElementArea(3e-08)
        Sub_mesh_face = Sub_mesh_face_m.GetSubMesh()
        smesh.SetName(Sub_mesh_face, 'Sub_mesh_face')
        mesh2D = Sub_mesh_face_m
        #faceIDs = viscous_layer_g.GetSubShapeIndices()  # todo, UnionIds
        faceIDs = geompy.GetObjectIDs(rotor_g) + geompy.GetObjectIDs(wall_g)
        ViscousLayers = mesh2D.ViscousLayers2D(bl_thickness, bl_numberOfLayers, bl_stretchFactor, faceIDs, isEdgesToIgnore=False)
        status = Mesh_1.AddHypothesis(ViscousLayers, back_g)
    else:  # apply directly to 2D domain
        ViscousLayers = mesh2D.ViscousLayers2D(bl_thickness, bl_numberOfLayers, bl_stretchFactor, viscous_layer_g.GetSubShapeIndices(), isEdgesToIgnore=False)


if using_3D:
    if False:
        Mesh_3D = Mesh_1.Tetrahedron(algo=smeshBuilder.NETGEN_3D)  # default 3D meshing method
        NETGEN_3D_Parameters = Mesh_3D.Parameters()
        NETGEN_3D_Parameters.SetMaxSize( 0.0005 )
        NETGEN_3D_Parameters.SetSecondOrder( 0 )
        NETGEN_3D_Parameters.SetOptimize( 1 )
        NETGEN_3D_Parameters.SetFineness( 2 )
        NETGEN_3D_Parameters.SetChordalError( 0.1 )
        NETGEN_3D_Parameters.SetChordalErrorEnabled( 0 )
        NETGEN_3D_Parameters.SetMinSize( 2e-05 )
        NETGEN_3D_Parameters.SetUseSurfaceCurvature( 1 )
        NETGEN_3D_Parameters.SetFuseEdges( 1 )
        NETGEN_3D_Parameters.SetQuadAllowed( 1 )
        smesh.SetName(Mesh_3D.GetAlgorithm(), 'Tetra_3D_netgen')
        smesh.SetName(Mesh_3D, 'Tetra_3D')
    else:
        Prism_3D = Mesh_1.Prism()
        algo_3D = Prism_3D.GetAlgorithm()
        smesh.SetName(algo_3D, 'algo_3D')
        smesh.SetName(Prism_3D, 'Prism_3D')

        if using_viscous_layers and False:
            ViscousLayers = algo_3D.ViscousLayers(bl_thickness, bl_numberOfLayers, bl_stretchFactor, viscous_layer_g.GetSubShapeIndices(), False)

    mesh_solid_type= SMESH.VOLUME
    mesh_boundary_type = SMESH.FACE
else:
    mesh_solid_type= SMESH.FACE
    mesh_boundary_type = SMESH.EDGE



smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(Sub_mesh_large, 'Sub_mesh_large')
smesh.SetName(Sub_mesh_vertical, 'Sub_mesh_vertical')

Mesh_1.SetMeshOrder([[Sub_mesh_large, Sub_mesh_vertical, Sub_mesh_small, Sub_mesh_face]])
###############################
isDone = Mesh_1.Compute()

#hole_region_1 = Mesh_1.GroupOnGeom(hole_region,'hole_region',mesh_solid_type)
#smesh.SetName(hole_region_1, 'hole_region')


inlet_1 = Mesh_1.GroupOnGeom(inlet_g,'inlet_g', mesh_boundary_type)
outlet_1 = Mesh_1.GroupOnGeom(outlet_g,'outlet_g', mesh_boundary_type)
wall_1 = Mesh_1.GroupOnGeom(wall_g,'wall_g', mesh_boundary_type)
if using_pressure_tapping_hole:
    tap_1 = Mesh_1.GroupOnGeom(tap_g,'tap_g', mesh_boundary_type)
rotor_1 = Mesh_1.GroupOnGeom(rotor_g,'rotor_g', mesh_boundary_type)

smesh.SetName(inlet_1, 'inlet')
smesh.SetName(outlet_1, 'outlet')
smesh.SetName(wall_1, 'wall')
smesh.SetName(rotor_1, 'rotor')
if using_pressure_tapping_hole:
    smesh.SetName(tap_1, 'tap')

front_1 = Mesh_1.GroupOnGeom(front_g,'frontb_g', mesh_boundary_type)
smesh.SetName(front_1, 'front')
back_1 = Mesh_1.GroupOnGeom(back_g,'back_g', mesh_boundary_type)
smesh.SetName(back_1, 'back')

#it is needed,otherwise, gmsh does not found any volume mesh, MED export option may control this 
cdomain = Mesh_1.GroupOnGeom(all_regions,'all_regions', mesh_solid_type)
smesh.SetName(cdomain, 'cdomain')
if False:
    upstream = Mesh_1.GroupOnGeom(upstream_regions,'upstream_regions', mesh_solid_type)
    smesh.SetName(cdomain, 'upstream')
    downstream = Mesh_1.GroupOnGeom(downstream_regions,'downstream_regions', mesh_solid_type)
    smesh.SetName(cdomain, 'downstream')

##################################
if exporting_fenics:
    if using_3D:
        Mesh_1.SplitVolumesIntoTetra( Mesh_1, 1)
    else:
        Mesh_1.QuadTo4Tri(Mesh_1)  # split for 2D mesh, it works!

    isDone = Mesh_1.Compute()

if exporting_unv:
    try:
        Mesh_1.ExportUNV(mesh_output_filename[:-4] + '.unv')   #cgns
    except:
        print('ExportPartToUNV() failed. Invalid file name?')

Mesh_1.ExportMED(mesh_output_filename, 0, SMESH.MED_V2_2, 1, None ,1)

print('==== completed mesh saving ====')

#meshio-convert Mesh_1.med test.xdmf  # support quad mesh
if salome.sg.hasDesktop():
    try:
        salome.sg.updateObjBrowser(True)  # salome v8
    except:
        salome.sg.updateObjBrowser()
else:
    from runSalome import *
    myArgs={}
    myArgs["killall"] = True
    kill_salome(myArgs)