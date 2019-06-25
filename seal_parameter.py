from __future__ import print_function, division

import math

###############################
# geometry parameter
exporting_unv = False  # CGNS UNV are accepted by icem-cfd
#exporting_foam = True  # CFX also accept singel layer 3D mesh as 2D case
# salome mesh to fluent:  using `foamMeshToFluent` only support 3D mesh
# symmetry/periodic to simulate the
# fluent native cas and dat files are supported by to paraview
using_true_3D = False
using_half_domain = False   # split the domain at the hole sym plane
simulating_jet_only = True
using_pressure_tapping_hole = False
exporting_single_layer_3D = not using_true_3D   # CFX, fluent, foam need that for 2D case
exporting_fenics = False
using_3D = using_true_3D or exporting_single_layer_3D
# foam must use 3D mesh for a 2D case, single layer

using_axisymmetric_mesh = False
using_quad_mesh = False

using_viscous_layers = True

mesh_output_filename = '/tmp/Mesh_1.med'
geom_filename = '/tmp/gap_seal.step'


#turning points, axis mesh has a requirement:
x0 = 0
y0 = 0
z0 = 0

#seal specific geometry, gap or labyrinth seal
# axis is X for FOAM,  Fluent
rotor_r = 1.0  # baseline, there can be some step
rotor_step_height = 0.003
rotor_step_width = 0.008
gap = 0.0005 # down to 0.25mm
#r_stator =  rotor_r + gap + tooth_hegiht + seal_thickness

#straight upright tooth
tooth_angle = 15 # deg
tooth_height = 0.02
tooth_height_smaller = tooth_height - rotor_step_height
tooth_thickness = 0.002
tooth_chamfer_height = tooth_thickness
tooth_group_width = 0.04 # including 2 teeth of different height
N_tooth_in_group = 2
inter_tooth_distance = tooth_group_width/N_tooth_in_group  # assume equal-distance

long_edge_length_threshold = tooth_height * 1.2
small_edge_length_threshold = rotor_step_width * 0.51

N_tooth_group = 1
seal_width = N_tooth_group*tooth_group_width
seal_thickness = 0.005
seal_center_x = x0 + seal_width*0.5
seal_max_x = x0 + seal_width
seal_min_x = x0
seal_origin = x0, rotor_r + gap + tooth_height, z0
rotor_max_y = rotor_r + rotor_step_height
rotor_min_y = rotor_r


#where is the local origin?
reference_length = gap*10
if simulating_jet_only:
    upstream_width = reference_length * 2
    downstream_width = reference_length * 2
else:
    upstream_width = reference_length * 1.1
    downstream_width = reference_length * 1.1
upstream_height = reference_length * 1.5 # x-axis, should be depend on angle
downstream_height = reference_length * 2.5

inlet_x = seal_min_x - upstream_width
inlet_y = seal_origin[1]  # same as seal starting corner, tooth root
outlet_x = seal_max_x + downstream_width
outlet_y = seal_origin[1]


#where is the local origin?
inlet_points = [(inlet_x, rotor_r), (inlet_x, inlet_y)]
outlet_points = [(outlet_x, rotor_r), (outlet_x, outlet_y)]

def generate_tooth_group_xy(i):
    # single unit for periodic profile, can be one tooth or two teeth with diff height
    start_x, start_y = seal_origin[0]+i*tooth_group_width, seal_origin[1]
    seal_group_points = [
    (start_x, start_y-tooth_height),
    (start_x+tooth_thickness, start_y-tooth_height+tooth_chamfer_height),
    (start_x+tooth_thickness, start_y),
    (start_x+inter_tooth_distance, start_y),
    (start_x+inter_tooth_distance, start_y-tooth_height_smaller),
    (start_x+inter_tooth_distance+tooth_thickness, start_y-tooth_height_smaller + tooth_chamfer_height),
    (start_x+inter_tooth_distance+tooth_thickness, start_y),
    (start_x+tooth_group_width, start_y)
    ]
    return seal_group_points

def generate_seal_xy(N=2):
    # only the tooth side of seal geometry profile is created here
    xylist = [(seal_origin[0], seal_origin[1])] # need the very first starting point
    for i in range(N):
        xylist += generate_tooth_group_xy(i)  #only + can merge two lists of tuples
    return xylist

def generate_seal_profile_xy():
    pass

def generate_rotor_segment_xy(i):
    # single unit for periodic profile, can be one tooth or two teeth with diff height
    # first group is numbered as zero
    start_x, start_y = seal_origin[0]+i*tooth_group_width, rotor_r
    return [
    (start_x+inter_tooth_distance-0.5*rotor_step_width, start_y),
    (start_x+inter_tooth_distance-0.5*rotor_step_width, start_y+rotor_step_height),
    (start_x+inter_tooth_distance, start_y+rotor_step_height),  # in order to refine mesh near the point
    (start_x+inter_tooth_distance+0.5*rotor_step_width, start_y+rotor_step_height),
    (start_x+inter_tooth_distance+0.5*rotor_step_width, start_y),
    (start_x+inter_tooth_distance, start_y),
    ]

def generate_rotor_xy(N=2):
    xylist = [(seal_origin[0], rotor_r)] 
    for i in range(N):
        xylist += generate_rotor_segment_xy(i)
    return xylist


if using_true_3D:
    extrusion_thickness = reference_length*5  # for 3D with tubing hole
else:
    extrusion_thickness = reference_length*0.1  # for 3D with tubing hole


#edge length threshold
if exporting_single_layer_3D:
    line_segment_nb_default = 30
    line_segment_nb_large = 80
    line_segment_nb_vertical = 1
else:  # real 3D case
    line_segment_nb_default = 24
    line_segment_nb_vertical = 24 # it is important to have exactly half default
    line_segment_nb_large = 50
line_segment_nb_small = 20

#########################################

#testing
if __name__ == "__main__":
    seal_points = generate_seal_xy(N_tooth_group)
    # turning the points position for different valve opening angle,   +cos(alpha)*r_stator
    rotor_points = generate_rotor_xy(N_tooth_group)

    print(seal_points)
    print(rotor_points)