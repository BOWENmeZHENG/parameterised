from visualization import *

import abaqus_utils as ut

# Constants
r_out = 0.3
r_in = 0.2
width = 0.1
spoke_width = 0.04
num_spokes = 3
meshsize = 0.03
r_depth = 0.02
r_pressure = 0.1
E = 1e8
mu = 0.3
load = 10000
results_location = 'C:/Users/bowen/Desktop/abaqus_python/parameterised/'

# Names
part_name = 'wheel'
material_name = 'wheel_material'
section_name = 'wheel_section'
assembly_name = 'wheel-assembly'
step_name = 'static_load'
load_name = 'compression'
bc_name = 'fixed'
job_name = 'wheel_compression'

# Derived values
s_pt_whole, s_pt_lateral, s_pt_extr, s_pt_out_edge, spoke_start, s_pts_spoke = ut.derived_values(r_in, r_out, width,
                                                                                                 spoke_width)

# Define wheel geometry
mymodel = mdb.models['Model-1']
mypart = ut.init_part(mymodel, r_out, r_in, width, part_name)
ut.spoke(mymodel, mypart, width, num_spokes, spoke_width, spoke_start, s_pts_spoke, s_pt_extr, s_pt_out_edge)

# set for exterior nodes
mypart.Set(faces=mypart.faces.getByBoundingSphere(center=(0, 0, 0), radius=10.0), name='all_faces')

# Material & Section
ut.mat_sect(mymodel, mypart, material_name, E, mu, section_name, s_pt_whole)

# Assembly
myassembly = ut.make_assembly(mymodel, mypart, assembly_name)

# Step
mymodel.StaticStep(name=step_name, previous='Initial')

# Mesh
ut.make_mesh(mypart, meshsize, s_pt_whole, r_out, width)

# Loading & BC
ut.load_bc(mymodel, mypart, myassembly, step_name, load_name, bc_name,
           r_out, width, r_depth, r_pressure, load, s_pt_lateral)

# Job
ut.job(job_name)

# Access results
odb_name = job_name + '.odb'
odb = openOdb(path=odb_name, readOnly=True)
odb_assembly = odb.rootAssembly
odb_instance = odb_assembly.instances.keys()[0]
odb_step1 = odb.steps.values()[0]
frame = odb.steps[odb_step1.name].frames[-1]
elemStress = frame.fieldOutputs['S']
odb_set_whole = odb_assembly.elementSets[' ALL ELEMENTS']
field = elemStress.getSubset(region=odb_set_whole, position=ELEMENT_NODAL)

nodalS11 = {}
for value in field.values:
    if value.nodeLabel in nodalS11:
        nodalS11[value.nodeLabel].append(value.data[0])
    else:
        nodalS11.update({value.nodeLabel: [value.data[0]]})
for key in nodalS11:
    nodalS11.update({key: sum(nodalS11[key]) / len(nodalS11[key])})

# Exterior nodes
node_object = mypart.sets['all_faces'].nodes
node_labels = [node.label for node in node_object]

# Print_result
with open(results_location + 'nodes.csv', 'w') as f:
    f.write('nodeid,nodetype,x,y,z,s11\n')
    for node_s11 in nodalS11.items():
        nodeid, s11 = node_s11[0], node_s11[-1]
        meshnode_object = mypart.nodes[nodeid - 1]
        x, y, z = meshnode_object.coordinates[0], meshnode_object.coordinates[1], meshnode_object.coordinates[2]
        if nodeid in node_labels:
            nodetype = 1
        else:
            nodetype = 0
        f.write('%d,%d,%f,%f,%f,%f\n' % (nodeid, nodetype, x, y, z, s11))

with open(results_location + 'elements.csv', 'w') as f:
    f.write('elementid,node1,node2,node3,node4\n')
    for element in mypart.elements:
        f.write('%d,%d,%d,%d,%d\n' % (element.label, element.connectivity[0], element.connectivity[1],
                                      element.connectivity[2], element.connectivity[3]))
