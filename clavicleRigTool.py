import maya.cmds as cmds
from master_rigger import renamerLibrary as name
from master_rigger import curve_assignment as crv
from master_rigger import basicTools as tool
from master_rigger import attributeManipulation as attr
from master_rigger import createNodeLibrary as node

clav_starting_position = [[1, 16, 1], [3, 17, 0]]

side_to_color = {
    'L': 'cyan',
    'left': 'cyan',
    'lt': 'cyan',
    'R': 'red',
    'right': 'red',
    'rt': 'red',
    'C': 'yellow',
    'center': 'yellow',
    'ctr': 'yellow'
}

module_attr_list = ['IKFK']
module_attribute_dict = {
    'IKFK': ['double', 0, 1, 0, True, None]
}


def create_clav_locators(prefix='L',):
    if 'right' in prefix or 'R' in prefix or 'rt' in prefix:
        clav_starting_position[0][0] = -clav_starting_position[0][0]
        clav_starting_position[1][0] = -clav_starting_position[1][0]

    base_loc = cmds.spaceLocator(name=prefix + '_clav_LOC')[0]
    end_loc = cmds.spaceLocator(name=prefix + '_clav_END_LOC')[0]

    cmds.xform(base_loc, translation=clav_starting_position[0])
    cmds.xform(end_loc, translation=clav_starting_position[1])

    clav_locator_list = [base_loc, end_loc]

    cmds.parent(end_loc, base_loc)

    clav_module = cmds.group(empty=True, name=prefix + '_clav_MOD')
    for attribute in module_attr_list:
        attr.create_attr(attribute,
                         attribute_type=module_attribute_dict[attribute][0],
                         input_object=clav_module,
                         min_value=module_attribute_dict[attribute][1],
                         max_value=module_attribute_dict[attribute][2],
                         default_value=module_attribute_dict[attribute][3],
                         keyable=module_attribute_dict[attribute][4],
                         enum_names=module_attribute_dict[attribute][5])

    attr.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, objects=[clav_module])

    return clav_locator_list


def build_clav_system(locator_inputs, prefix='L', orient_symmetry=False,
                      fk_shape='ring', ik_shape='plus'):
    input_node = tool.create_offset(suffix='temp',
                                    input_object=locator_inputs[0])
    input_mod = cmds.rename(input_node, prefix + '_clav_input_MOD')
    output_mod = cmds.group(empty=True, name=prefix + '_clav_output_MOD')

    clav_module = prefix + '_clav_MOD'
    cmds.parent(input_mod, output_mod, clav_module)

    cmds.select(clear=True)
    clav_bone_list = []
    for loc in locator_inputs:
        locator_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
        bone = cmds.joint(name=loc.replace('LOC', 'BONE'),
                          position=[locator_position[0],
                          locator_position[1],
                          locator_position[2]])
        clav_bone_list.append(bone)

    # Orient Bones (to world)
    cmds.joint(clav_bone_list[0],
               edit=True,
               orientJoint='none',
               children=True)

    # FK system
    fk_origin = cmds.duplicate(clav_bone_list[0], renameChildren=True)
    fk_joints = name.search_replace_name(search_input='BONE1',
                                         replace_output='FK_JNT',
                                         scope='selection',
                                         input_object=fk_origin)

    # IK system
    ik_origin = cmds.duplicate(clav_bone_list[0], renameChildren=True)
    ik_joints = name.search_replace_name(search_input='BONE1',
                                         replace_output='IK_JNT',
                                         scope='selection',
                                         input_object=ik_origin)

    ik_handle = cmds.ikHandle(startJoint=ik_joints[0],
                              endEffector=ik_joints[-1],
                              solver='ikSCsolver',
                              name=prefix + '_clav_IKH')[0]

    # Variable to assign the symmetry -1 scale assignment
    inverse = None
    if orient_symmetry:
        inverse = 'x'

    # Controls
    fk_ctrl = cmds.group(empty=True, name=fk_joints[0].replace('JNT', 'CTRL'))
    crv.add_curve_shape(shape_choice=fk_shape,
                        transform_node=fk_ctrl,
                        color=side_to_color[prefix],
                        shape_offset=[90, 0, 0])
    fk_offset = tool.create_offset(input_object=fk_ctrl, invert_scale=inverse)
    tool.match_transformations(source=fk_joints[0], target=fk_offset)

    ik_ctrl = cmds.group(empty=True, name=ik_joints[0].replace('JNT', 'CTRL'))
    crv.add_curve_shape(shape_choice=ik_shape,
                        transform_node=ik_ctrl,
                        color=side_to_color[prefix],
                        shape_offset=[0, 0, 90])
    ik_offset = tool.create_offset(input_object=ik_ctrl, invert_scale=inverse)
    tool.match_transformations(source=ik_joints[-1], target=ik_offset)

    # Line if shape needs to be rotated to deal with perspective
    attr.lock_hide(0, 0, 0, 1, 1, 1, 1, 1, 1, 1, objects=[ik_ctrl])
    attr.lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1, objects=[fk_ctrl])

    # Connections
    cmds.parentConstraint(fk_ctrl, fk_joints[0], maintainOffset=True)
    cmds.parentConstraint(ik_ctrl, ik_handle, maintainOffset=True)

    clav_ikfk = cmds.parentConstraint(fk_joints[0],
                                      ik_joints[0],
                                      clav_bone_list[0],
                                      maintainOffset=True)[0]

    ikfk_rev = node.create_node('REV', name=prefix + '_clav_IKFK')
    weight_0_attr = cmds.listAttr(clav_ikfk)[-2]
    weight_1_attr = cmds.listAttr(clav_ikfk)[-1]
    cmds.connectAttr(clav_module + '.IKFK',
                     '%s.%s' % (clav_ikfk, weight_1_attr))
    cmds.connectAttr(clav_module + '.IKFK', ikfk_rev + '.inputX')
    cmds.connectAttr(ikfk_rev + '.outputX',
                     '%s.%s' % (clav_ikfk, weight_0_attr))

    jnt_grp = cmds.group(ik_joints[0], fk_joints[0],
                         name=prefix + '_clav_JNT_GRP')
    bone_grp = cmds.group(clav_bone_list[0], name=prefix + '_clav_BONE_GRP')
    ctrl_grp = cmds.group(ik_offset, fk_offset, name=prefix + '_clav_CTRL_GRP')
    parts_grp = cmds.group(ik_handle, name=prefix + '_clav_PARTS_GRP')
    cmds.parent(jnt_grp, bone_grp, ctrl_grp, parts_grp, input_mod)

    output_node = tool.create_child(suffix='temp',
                                    input_object=clav_bone_list[-1])
    output_srt = cmds.rename(output_node, prefix + '_clav_output_SRT')

    output_dcpm = node.create_node('DCPM', name=output_srt)
    cmds.connectAttr(output_srt + '.worldMatrix[0]',
                     output_dcpm + '.inputMatrix')
    cmds.connectAttr(output_dcpm + '.outputTranslate',
                     output_mod + '.translate')
    cmds.connectAttr(output_dcpm + '.outputRotate',
                     output_mod + '.rotate')
    cmds.connectAttr(output_dcpm + '.outputScale',
                     output_mod + '.scale')

    cmds.delete(locator_inputs)
