import maya.cmds as cmds

from master_rigger import curve_assignment as crv
from master_rigger import createNodeLibrary as node


def lock_hide(tx, ty, tz, rx, ry, rz, sx, sy, sz, v):
    a = 0
    attr_type = [tx, ty, tz, rx, ry, rz, sx, sy, sz, v]
    for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v']:
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
    crv.set_control_color('yellow', input_object=local_master)
    global_master = cmds.group(em=True, n=ctrl_setup_names[0] + '_CTRL')
    crv.add_curve_shape('quad_arrow', transform_node=global_master, color='yellow')
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
    global_matrix = node.create_node('DCPM', name='GLOBAL')
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
