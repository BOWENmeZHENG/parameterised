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


def derived_values(r_in, r_out, width, spoke_width):
    s_pt_whole = (0.0, r_out, width / 2)
    s_pt_lateral = (0.0, r_out, width / 2)
    s_pt_extr = (0.0, (r_in + r_out) / 2, width)
    s_pt_out_edge = (0.0, r_out, width)
    spoke_start = (r_out + r_in) / 2
    s_pts_spoke = [(-spoke_start + 0.01, spoke_width / 2),
                   (-spoke_start + 0.01, -spoke_width / 2),
                   (-spoke_start, 0),
                   (spoke_start, 0)]
    return s_pt_whole, s_pt_lateral, s_pt_extr, s_pt_out_edge, spoke_start, s_pts_spoke


def init_part(mymodel, r_out, r_in, width, part_name):
    mymodel.ConstrainedSketch(name='__profile__', sheetSize=r_out * 2)
    mymodel.sketches['__profile__'].CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_out, 0.0))
    mymodel.sketches['__profile__'].CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_in, 0.0))
    mymodel.Part(dimensionality=THREE_D, name=part_name, type=DEFORMABLE_BODY)
    mypart = mymodel.parts[part_name]
    mypart.BaseSolidExtrude(depth=width, sketch=mymodel.sketches['__profile__'])
    del mymodel.sketches['__profile__']
    return mypart


def spoke(mymodel, mypart, width, num_spokes, spoke_width, spoke_start, s_pts_spoke, s_pt_extr, s_pt_out_edge):
    face_base = mypart.faces.findAt((s_pt_extr,), )[0]
    edge_extrusion = mypart.edges.findAt((s_pt_out_edge,), )[0]
    mymodel.ConstrainedSketch(gridSpacing=0.04, name='__profile__', sheetSize=1.7,
                              transform=mypart.MakeSketchTransform(
                                  sketchPlane=face_base, sketchPlaneSide=SIDE1, sketchUpEdge=edge_extrusion,
                                  sketchOrientation=RIGHT, origin=(0.0, 0.0, width)))
    mysketch = mymodel.sketches['__profile__']
    mypart.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=mysketch)
    mysketch.rectangle(point1=(-spoke_start, -spoke_width / 2), point2=(spoke_start, spoke_width / 2))
    mypart.SolidExtrude(depth=width, flipExtrudeDirection=ON, sketch=mysketch, sketchOrientation=RIGHT,
                        sketchPlane=face_base, sketchPlaneSide=SIDE1, sketchUpEdge=edge_extrusion)
    del mysketch

    for i in range(num_spokes - 1):
        face_base = mypart.faces.findAt((s_pt_extr,), )[0]
        edge_extrusion = mypart.edges.findAt((s_pt_out_edge,), )[0]
        mymodel.ConstrainedSketch(gridSpacing=0.04, name='__profile__', sheetSize=1.7,
                                  transform=mypart.MakeSketchTransform(
                                      sketchPlane=face_base, sketchPlaneSide=SIDE1, sketchUpEdge=edge_extrusion,
                                      sketchOrientation=RIGHT, origin=(0.0, 0.0, width)))
        mysketch = mymodel.sketches['__profile__']
        mypart.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=mysketch)
        mysketch.rectangle(point1=(-spoke_start, -spoke_width / 2), point2=(spoke_start, spoke_width / 2))
        mysketch.rotate(angle=180/num_spokes*(i + 1), centerPoint=(0.0, 0.0),
                        objectList=(
                            mysketch.geometry.findAt(s_pts_spoke[0], ),
                            mysketch.geometry.findAt(s_pts_spoke[1], ),
                            mysketch.geometry.findAt(s_pts_spoke[2], ),
                            mysketch.geometry.findAt(s_pts_spoke[3], )))
        mypart.SolidExtrude(depth=width, flipExtrudeDirection=ON, sketch=mysketch, sketchOrientation=RIGHT,
                            sketchPlane=face_base, sketchPlaneSide=SIDE1, sketchUpEdge=edge_extrusion)
        del mysketch