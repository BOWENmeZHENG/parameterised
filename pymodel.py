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

# Constants
r_out = 0.3
r_in = 0.2
width = 0.1
meshsize = 0.02
r_depth = 0.02
r_pressure = 0.1
search_point = (0.0, r_out, width/2)

mymodel = mdb.models['Model-1']
mymodel.ConstrainedSketch(name='__profile__', sheetSize=r_out*2)
mymodel.sketches['__profile__'].CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_out, 0.0))
mymodel.sketches['__profile__'].CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_in, 0.0))
mymodel.Part(dimensionality=THREE_D, name='Part-1', type=DEFORMABLE_BODY)

mypart = mdb.models['Model-1'].parts['Part-1']
mypart.BaseSolidExtrude(depth=width, sketch=mymodel.sketches['__profile__'])
del mymodel.sketches['__profile__']

mypart.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=meshsize)
mypart.setMeshControls(elemShape=TET, regions=mypart.cells.findAt((search_point,), ), technique=FREE)
mypart.setElementType(elemTypes=(ElemType(elemCode=C3D8R, elemLibrary=STANDARD),
                                 ElemType(elemCode=C3D6, elemLibrary=STANDARD),
                                 ElemType(elemCode=C3D4, elemLibrary=STANDARD,
                                          secondOrderAccuracy=OFF, distortionControl=DEFAULT)),
                      regions=(mypart.cells.findAt(((0.0, r_out, width/2),), ),))
mypart.generateMesh()

# get face by coordinates

mypart.Set(faces=mypart.faces.findAt((search_point,), ), name='face_big')
face_big = mypart.sets['face_big'].faces[0]
mypart.Set(nodes=face_big.getNodes(), name='face_nodes')
face_big_nodes = mypart.sets['face_nodes'].nodes
mypart.Set(nodes=face_big_nodes.getByBoundingCylinder(center1=(0.0, r_out-r_depth, width/2),
                                                      center2=(0.0, r_out+r_depth, width/2),
                                                      radius=r_pressure), name='nodes_load')
