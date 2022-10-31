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


def derived_values(r_in, r_out, width, num_spokes, spoke_width):
    s_pt_whole = (0.0, r_out, width / 2)
    s_pt_lateral = (0.0, r_out, width / 2)
    s_pt_extr = (0.0, (r_in + r_out) / 2, width)
    s_pt_out_edge = (0.0, r_out, width)

    spoke_start = (r_out + r_in) / 2
    s_pts_spoke = [(-spoke_start + 0.01, spoke_width / 2),
                   (-spoke_start + 0.01, -spoke_width / 2),
                   (-spoke_start, 0),
                   (spoke_start, 0)]

    rot_angle = 180 / num_spokes

    return s_pt_whole, s_pt_lateral, s_pt_extr, s_pt_out_edge, spoke_start, s_pts_spoke, rot_angle


def init_part(mymodel, r_out, r_in, width, part_name):
    mymodel.ConstrainedSketch(name='__profile__', sheetSize=r_out * 2)
    mymodel.sketches['__profile__'].CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_out, 0.0))
    mymodel.sketches['__profile__'].CircleByCenterPerimeter(center=(0.0, 0.0), point1=(r_in, 0.0))
    mymodel.Part(dimensionality=THREE_D, name=part_name, type=DEFORMABLE_BODY)
    mypart = mymodel.parts[part_name]
    mypart.BaseSolidExtrude(depth=width, sketch=mymodel.sketches['__profile__'])
    del mymodel.sketches['__profile__']
    return mypart
