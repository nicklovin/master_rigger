import maya.cmds as cmds
from functools import partial


# Global variables, lists, and dictionaries
attributes = ['.tx', '.ty', '.tz', 
              '.rx', '.ry', '.rz', 
              '.sx', '.sy', '.sz', 
              '.v']
# colors + values
rgb_dictionary = {
    'red': [1, 0, 0],
    'orange': [1, .4, 0],
    'yellow': [1, 1, 0],
    'green': [0, 1, 0],
    'cyan': [0, 1, 1],
    'blue': [0, 0, 1],
    'magenta': [1, 0, 1],
    'purple': [1, 0, 1],
    'white': [1, 1, 1],
}

# Multi-shaped controls (require separate definitions)


def control_sphere(*arg):
    circle_1 = cmds.circle(nr=[0, 1, 0], r=1, d=3, ch=0)
    circle_2 = cmds.circle(nr=[1, 0, 0], r=1, d=3, ch=0)
    circle_3 = cmds.circle(nr=[0, 0, 1], r=1, d=3, ch=0)

    cmds.parent(cmds.listRelatives(circle_2, circle_3, shapes=True), circle_1,
                s=True, r=True)
    cmds.delete(circle_2, circle_3)
    return circle_1


# Curve point dictionary that creates curve shape node to be put into a
# transform control node.  This make it easier to allow curve choices later.
curve_library = {
    'circle': partial(cmds.circle,
                      normal=[0, 1, 0],
                      radius=1,
                      degree=3,
                      sections=16,
                      constructionhistory=False),
    'square': partial(cmds.curve,
                      degree=1,
                      point=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]),
    'triangle': partial(cmds.curve,
                        degree=1,
                        point=[(-1, 0, 1), (0, 0, -1), (1, 0, 1)]),
    'octagon': partial(cmds.circle,
                       normal=[0, 1, 0],
                       radius=1,
                       degree=1,
                       sections=8,
                       constructionhistory=False),
    'box': partial(cmds.curve,
                   degree=1,
                   point=[(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5),
                          (0.5, 0.5, -0.5,), (0.5, 0.5, 0.5,),
                          (0.5, -0.5, 0.5,),
                          (0.5, -0.5, -0.5,), (0.5, 0.5, -0.5,),
                          (-0.5, 0.5, -0.5,), (-0.5, -0.5, -0.5,),
                          (-0.5, -0.5, 0.5,), (-0.5, 0.5, 0.5,),
                          (-0.5, -0.5, 0.5,), (0.5, -0.5, 0.5,),
                          (0.5, -0.5, -0.5,), (-0.5, -0.5, -0.5,)]),
    'sphere': control_sphere,
    'pyramid': partial(cmds.curve,
                       degree=1,
                       point=[(9.27258e-008, -0.353553, -0.707107), (-0.707107,
                              -0.353553, -6.18172e-008), (0, 0.353553, 0),
                              (9.27258e-008, -0.353553, -0.707107), (0.707107,
                              -0.353553, 0), (0, 0.353553, 0), (-3.09086e-008,
                              -0.353553, 0.707107), (0.707107, -0.353553, 0),
                              (-3.09086e-008, -0.353553, 0.707107), (-0.707107,
                              -0.353553, -6.18172e-008)]),
    'diamond': partial(cmds.curve,
                       degree=1,
                       point=[(0, 1, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0),
                              (0, 0, -1), (-1, 0, 0), (0, 1, 0), (0, 0, 1),
                              (-1, 0, 0), (0, -1, 0), (0, 0, 1), (1, 0, 0),
                              (0, -1, 0), (0, 0, -1), (1, 0, 0)]),
    'quad_arrow': partial(cmds.curve,
                          degree=1,
                          p=[(0.4, 0.0, -0.4), (0.4, 0.0, -0.6),
                              (0.4, 0.0, -0.8), (0.4, 0.0, -1.0),
                              (0.4, 0.0, -1.2), (0.8, 0.0, -1.2),
                              (0.6, 0.0, -1.4), (0.4, 0.0, -1.6),
                              (0.2, 0.0, -1.8), (0.0, 0.0, -2.0),
                              (-0.2, 0.0, -1.8), (-0.4, 0.0, -1.6),
                              (-0.6, 0.0, -1.4), (-0.8, 0.0, -1.2),
                              (-0.4, 0.0, -1.2), (-0.4, 0.0, -1.0),
                              (-0.4, 0.0, -0.8), (-0.4, 0.0, -0.6),
                              (-0.4, 0.0, -0.4), (-0.6, 0.0, -0.4),
                              (-0.8, 0.0, -0.4), (-1.0, 0.0, -0.4),
                              (-1.2, 0.0, -0.4), (-1.2, 0.0, -0.6),
                              (-1.2, 0.0, -0.8), (-1.4, 0.0, -0.6),
                              (-1.6, 0.0, -0.4), (-1.8, 0.0, -0.2),
                              (-2.0, 0.0, 0.0),
                              (-1.8, 0.0, 0.2), (-1.6, 0.0, 0.4),
                              (-1.4, 0.0, 0.6), (-1.2, 0.0, 0.8),
                              (-1.2, 0.0, 0.4), (-1.0, 0.0, 0.4),
                              (-0.8, 0.0, 0.4), (-0.6, 0.0, 0.4),
                              (-0.4, 0.0, 0.4), (-0.4, 0.0, 0.6),
                              (-0.4, 0.0, 0.8), (-0.4, 0.0, 1.0),
                              (-0.4, 0.0, 1.2), (-0.8, 0.0, 1.2),
                              (-0.6, 0.0, 1.4), (-0.4, 0.0, 1.6),
                              (-0.2, 0.0, 1.8), (0.0, 0.0, 2.0),
                              (0.2, 0.0, 1.8), (0.4, 0.0, 1.6),
                              (0.6, 0.0, 1.4), (0.8, 0.0, 1.2), (0.4, 0.0, 1.2),
                              (0.4, 0.0, 1.0), (0.4, 0.0, 0.8), (0.4, 0.0, 0.6),
                              (0.4, 0.0, 0.4), (0.6, 0.0, 0.4), (0.8, 0.0, 0.4),
                              (1.0, 0.0, 0.4), (1.2, 0.0, 0.4), (1.2, 0.0, 0.8),
                              (1.4, 0.0, 0.6), (1.6, 0.0, 0.4), (1.8, 0.0, 0.2),
                              (2.0, 0.0, 0.0),
                              (1.8, 0.0, -0.2), (1.6, 0.0, -0.4),
                              (1.4, 0.0, -0.6), (1.2, 0.0, -0.8),
                              (1.2, 0.0, -0.6), (1.2, 0.0, -0.4),
                              (1.0, 0.0, -0.4), (0.8, 0.0, -0.4),
                              (0.6, 0.0, -0.4)]),

    'arrow': partial(cmds.curve,
                     degree=1,
                     p=[(-1, 0, -3), (-1, 0, -3), (-1, 0, -3), (-2, 0, -3),
                        (-2, 0, -3), (-2, 0, -3), (-2, 0, -3), (0, 0, -5),
                        (0, 0, -5), (0, 0, -5), (0, 0, -5), (2, 0, -3),
                        (2, 0, -3), (2, 0, -3), (2, 0, -3), (1, 0, -3),
                        (1, 0, -3), (1, 0, -3), (1, 0, -3), (1, 0, -2),
                        (1, 0, -1), (1, 0, 0), (1, 0, 1), (1, 0, 2),
                        (1, 0, 3), (1, 0, 3), (1, 0, 3), (1, 0, 3),
                        (-1, 0, 3), (-1, 0, 3), (-1, 0, 3), (-1, 0, 3),
                        (-1, 0, 2), (-1, 0, 1), (-1, 0, 0), (-1, 0, -1),
                        (-1, 0, -2)]),
    'plus': partial(cmds.curve,
                    degree=1,
                    p=[(-1, 0, -1), (-1, 0, -3), (1, 0, -3), (1, 0, -1),
                       (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3),
                       (-1, 0, 3), (-1, 0, 1), (-3, 0, 1), (-3, 0, -1)]),
    'ring': partial(cmds.curve,
                    d=1,
                    p=[(0.707107, 0.1, 0.707107), (1, 0.1, 0), (1, -0.1, 0),
                       (0.707107, -0.1, -0.707107), (0.707107, 0.1,
                       -0.707107), (0, 0.1, -1), (0, -0.1, -1), (-0.707107,
                       -0.1, -0.707107), (-0.707107, 0.1, -0.707107), (-1,
                       0.1, 0), (-1, -0.1, 0), (-0.707107, -0.1, 0.707107),
                       (-0.707107, 0.1, 0.707107), (0, 0.1, 1), (0, -0.1, 1),
                       (0.707107, -0.1, 0.707107), (0.707107, 0.1, 0.707107),
                       (0, 0.1, 1), (0, -0.1, 1), (-0.707107, -0.1,
                       0.707107), (-0.707107, 0.1, 0.707107), (-1, 0.1, 0),
                       (-1, -0.1, 0), (-0.707107, -0.1, -0.707107),
                       (-0.707107, 0.1, -0.707107), (0, 0.1, -1), (0, -0.1,
                       -1), (0.707107, -0.1, -0.707107), (0.707107, 0.1,
                       -0.707107), (1, 0.1, 0), (1, -0.1, 0), (0.707107,
                       -0.1, 0.707107)])
}
# Related to the above dictionary, this helps reduce the CVs created
curve_library_bool = {
    'circle': False,
    'square': True,
    'triangle': True,
    'octagon': False,
    'box': False,
    'sphere': False,
    'pyramid': False,  # might be True
    'diamond': False,  # might be True
    'quad_arrow': True,
    'arrow': True,
    'plus': True,
    'ring': True
}


def add_curve_shape(shape_choice, transform_node=None):
    # curve library calling
    if not transform_node:
        transform_node = cmds.ls(selection=True)[0]

    curve_transform = curve_library[shape_choice]()
    curve_shape = cmds.listRelatives(curve_transform, shapes=True)
    if curve_library_bool[shape_choice]:
        cmds.closeCurve(curve_shape, ch=0, replaceOriginal=1)
    cmds.parent(curve_shape, transform_node, shape=True, r=True)
    cmds.rename(curve_shape, transform_node + '_Shape')
    cmds.delete(curve_transform)


def set_color(rgb_input):
    # setting the color value based on the passed argument
    if rgb_input in rgb_dictionary:
        rgb = rgb_dictionary[rgb_input]
    else:
        rgb = cmds.colorEditor(query=True, rgb=True)
    
    cmds.setAttr('.overrideEnabled', 1)
    cmds.setAttr('.overrideRGBColors', 1)
    cmds.setAttr('.overrideColorR', rgb[0])
    cmds.setAttr('.overrideColorG', rgb[1])
    cmds.setAttr('.overrideColorB', rgb[2])


def lock_hide(tx, ty, tz, rx, ry, rz, sx, sy, sz, v):
    a = 0
    attr_type = [tx, ty, tz, rx, ry, rz, sx, sy, sz, v]
    for attr in attributes:
        if attr_type[a] == 1:
            cmds.setAttr(attr, lock=False, keyable=True)
        else:
            cmds.setAttr(attr, lock=True, keyable=False)
        a = a + 1
        
        
def simple_rig_setup(rig_name):  # input as needed
    ctrl_setup_names = ['Global', 'Local']
    hierarchy_names = ['GLOBAL_MOVE', 'IK', 'CTRL', 'JNT', 'BONE', 'DRIVER', 
                       'GEO', 'PROXY', 'RENDER', 'SPACE', 'MISC_NODES', 
                       'PLACEMENT', 'SCRIPT_NODES', 'DEFORMER', 
                       'DEFORMER_HANDLE', 'NONSCALE_JNTS', 'BLENDSHAPES']
    group_names = []
        
    local_master = cmds.circle(n=ctrl_setup_names[1] + '_CTRL', ch=False, 
                               nr=[0, 1, 0], r=3)
    set_color('yellow')
    global_master = quad_arrow(ctrl_setup_names[0] + '_CTRL')
    set_color('yellow')
    rig = cmds.group(em=True, n=rig_name)
    
    for g in hierarchy_names:
        grp = cmds.group(em=True, n=g + '_GRP')
        group_names.append(grp)
        cmds.parent(grp, rig)

    # global move grp
    cmds.parent(group_names[1], group_names[2], group_names[3], group_names[0]) 
    # joint type grp
    cmds.parent(group_names[4], group_names[5], group_names[3]) 
    # geo type grp
    cmds.parent(group_names[7], group_names[8], group_names[6]) 
    # spaces under local
    cmds.parent(group_names[9], local_master) 
    # deformer type grp
    cmds.parent(group_names[-1], group_names[-2], group_names[-3], 
                group_names[-4])
    # local under global
    cmds.parent(local_master, global_master) 
    # global under placement
    cmds.parent(global_master, group_names[11])
    # connecting global move parts to the matrix of the master controllers
    global_matrix = cmds.shadingNode('decomposeMatrix',
                                     asUtility=True,
                                     name='global_DCMX')
    cmds.connectAttr(local_master[0] + '.worldMatrix[0]',
                     global_matrix + '.inputMatrix')
    cmds.connectAttr(global_matrix + '.outputTranslate',
                     group_names[0] + '.translate')
    cmds.connectAttr(global_matrix + '.outputRotate', group_names[0] + '.rotate')
    cmds.connectAttr(global_matrix + '.outputScale', group_names[0] + '.scale')
    # set geo grp to reference by default
    cmds.setAttr(group_names[6] + '.overrideEnabled', 1)
    cmds.setAttr(group_names[6] + '.overrideDisplayType', 2)
    
    # add attrs to global and local + set connections
    cmds.addAttr(local_master, ln='localScale', at='double', dv=1)
    cmds.setAttr(local_master[0] + '.localScale', keyable=True)
    for s in ['X', 'Y', 'Z']:
        cmds.connectAttr(local_master[0] + '.localScale', 
                         local_master[0] + '.scale' + s)
    cmds.select(local_master[0])
    lock_hide(1, 1, 1, 1, 1, 1, 0, 0, 0, 0)
    
    cmds.addAttr(global_master, ln='globalScale', at='double', dv=1)
    cmds.addAttr(global_master, ln='_', nn=' ', at='enum', en='GEO:')
    cmds.addAttr(global_master, ln='geoVis', at='enum', en='Proxy:Render:', dv=1)
    cmds.setAttr(global_master + '.globalScale', keyable=True)
    cmds.setAttr(global_master + '._', keyable=False, lock=True, cb=True)
    cmds.setAttr(global_master + '.geoVis', keyable=False, cb=True)
    for s in ['X', 'Y', 'Z']:
        cmds.connectAttr(global_master + '.globalScale', 
                         global_master + '.scale' + s)
    cmds.select(global_master)
    lock_hide(1, 1, 1, 1, 1, 1, 0, 0, 0, 0)
    return global_master, local_master
