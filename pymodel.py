from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

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
s_pt_whole, s_pt_lateral, s_pt_extr, s_pt_out_edge, spoke_start, s_pts_spoke = ut.derived_values(r_in, r_out, width, spoke_width)

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
mypart.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=meshsize)
mypart.setMeshControls(elemShape=TET, regions=mypart.cells.findAt((s_pt_whole,), ), technique=FREE)
mypart.setElementType(elemTypes=(ElemType(elemCode=C3D8R, elemLibrary=STANDARD),
                                 ElemType(elemCode=C3D6, elemLibrary=STANDARD),
                                 ElemType(elemCode=C3D4, elemLibrary=STANDARD,
                                          secondOrderAccuracy=OFF, distortionControl=DEFAULT)),
                      regions=(mypart.cells.findAt(((0.0, r_out, width / 2),), ),))
mypart.generateMesh()

# get nodes for loading and BC
mypart.Set(faces=mypart.faces.findAt((s_pt_lateral,), ), name='face_big')
face_big = mypart.sets['face_big'].faces[0]
mypart.Set(nodes=face_big.getNodes(), name='face_nodes')
face_big_nodes = mypart.sets['face_nodes'].nodes
mypart.Set(nodes=face_big_nodes.getByBoundingCylinder(center1=(0.0, r_out - r_depth, width / 2),
                                                      center2=(0.0, r_out + r_depth, width / 2),
                                                      radius=r_pressure), name='nodes_load')
nodes_load = mypart.sets['nodes_load'].nodes
mypart.Set(nodes=face_big_nodes.getByBoundingCylinder(center1=(0.0, -(r_out - r_depth), width / 2),
                                                      center2=(0.0, -(r_out + r_depth), width / 2),
                                                      radius=r_pressure), name='nodes_bc')
nodes_bc = mypart.sets['nodes_bc'].nodes

# Load & BC
num_nodes_load = len(nodes_load)
mymodel.ConcentratedForce(cf2=-load/num_nodes_load, createStepName=step_name,
                          distributionType=UNIFORM, field='', localCsys=None, name=load_name,
                          region=myassembly.sets['nodes_load'])
mymodel.EncastreBC(createStepName=step_name, localCsys=None, name=bc_name, region=myassembly.sets['nodes_bc'])

# Job
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE,
        getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE,
        model='Model-1', modelPrint=OFF, multiprocessingMode=DEFAULT, name=job_name,
        nodalOutputPrecision=SINGLE, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='',
        type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
mdb.jobs[job_name].submit(consistencyChecking=OFF)

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
