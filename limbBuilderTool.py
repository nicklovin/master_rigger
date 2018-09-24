import maya.cmds as cmds
import pprint  # only for testing purposes, remove when completed
from string import ascii_uppercase
from master_rigger import curve_assignment as crv
from master_rigger import basicTools as tool
from master_rigger import renamerLibrary as name
from master_rigger import attributeManipulation as attr
from master_rigger import createNodeLibrary as node
reload(name)
reload(tool)
reload(node)


LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}

arm_parts = ['shoulder', 'elbow', 'wrist']
limb_starting_position = {
    'arm': [3, 17, 0],
    'leg': [2, 9, 0]
}
leg_parts = ['femur', 'knee', 'ankle']
limb_locator_list = []
pivot_locator_list = []
pv_locator_list = []

# For coloring controls based on side
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

module_attr_list = ['IKFK', 'bendyIK', 'foreLimbTwist']
module_attribute_dict = {
    'IKFK': ['double', 0, 1, 0, True, None],
    'bendyIK': ['double', 0, 1, 0, True, None],
    'foreLimbTwist': ['double', 0, 1, 0.75, True, None],
}
ik_end_attr_list = ['stretchy', 'secondaryVisibility']
ik_end_attribute_dict = {
    'stretchy': ['double', 0, 1, 0, True, None],
    'secondaryVisibility': ['bool', None, None, 0, False, None],
}

other_parts = []
fk_joints_list = []
fk_ctrl_offset = []
ik_joints_list = []
ik_ctrl_grp_list = []
limb_bone_list = []
limb_dict = {}


def build_limb_library(prefix='L', limb_type='arm', extra_joints=2,
                       auto_twist=True):

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_parts = None
        pass  # Add other_parts to this, but only after other parts are added

    for part in limb_parts:
        # finger = finger + 1
        # finger_letter = LETTERS_INDEX[finger]
        limb_key = '%s_%s' % (prefix, part)
        limb_section_list = []
        if part == limb_parts[2]:
            # Make sure the wrist/ankle do not get extension pieces
            limb_section_list.append(limb_key)
            limb_dict[part] = limb_section_list
            continue
        if extra_joints > 0:
            for section in range(extra_joints + 1):
                if section == 0:
                    # Setting the base point (key) in the key's list
                    limb_section_list.append(limb_key)
                    continue
                segment = LETTERS_INDEX[section]

                limb_section_list.append('%s_%s_%s'
                                         % (prefix, part, segment))
        else:
            limb_section_list.append(limb_key)
        limb_dict[part] = limb_section_list
    # fingers_dict[finger_key] = finger_segment_list
    pprint.pprint(limb_dict)
    return limb_dict


def create_limb_locators(prefix='L', limb_type='arm'):

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_parts = None
        pass  # Add other_parts to this, but only after other parts are added

    parent_loc = None
    distance_factor = 4.0 / len(limb_dict[limb_parts[0]])  # 4=default distance
    i = 1
    for segment in limb_parts:
        # Using the limb_parts list keeps the correct order when calling the
        # limb_dict
        for part in limb_dict[segment]:
            segment_loc = cmds.spaceLocator(name=part + '_LOC')[0]
            if parent_loc:
                cmds.parent(segment_loc, parent_loc)
                cmds.xform(segment_loc,
                           translation=[distance_factor * i, 0, 0],
                           absolute=True)
                i = i + 1
            else:
                cmds.xform(segment_loc,
                           translation=limb_starting_position[limb_type],
                           worldSpace=True)
            # If the locator is the first of the part (key), make its color
            # significant
            if part.endswith(segment):
                crv.set_control_color(rgb_input='yellow',
                                      input_object=segment_loc + 'Shape')
                pivot_locator_list.append(segment_loc)
                parent_loc = segment_loc
                i = 1  # Reset the distance index factor
            else:
                cmds.setAttr(segment_loc + '.localScaleX', 0.5)
                cmds.setAttr(segment_loc + '.localScaleY', 0.5)
                cmds.setAttr(segment_loc + '.localScaleZ', 0.5)
            limb_locator_list.append(segment_loc)

    # Setting the constraints for in-between locators
    i = 1.0
    weight_factor = float(len(limb_dict[limb_parts[0]]))
    for loc in limb_locator_list:
        if loc not in pivot_locator_list:
            if limb_parts[0] in loc:
                pos_cns = cmds.pointConstraint(pivot_locator_list[0],
                                               pivot_locator_list[1],
                                               loc,
                                               maintainOffset=False)[0]
                cmds.setAttr('%s.%sW0' % (pos_cns, pivot_locator_list[0]),
                             1 - (i / weight_factor))
                cmds.setAttr('%s.%sW1' % (pos_cns, pivot_locator_list[1]),
                             i / weight_factor)
            elif limb_parts[1] in loc:
                pos_cns = cmds.pointConstraint(pivot_locator_list[1],
                                               pivot_locator_list[2],
                                               loc,
                                               maintainOffset=False)[0]
                cmds.setAttr('%s.%sW0' % (pos_cns, pivot_locator_list[1]),
                             1 - (i / weight_factor))
                cmds.setAttr('%s.%sW1' % (pos_cns, pivot_locator_list[2]),
                             i / weight_factor)

            i = i + 1
            if i >= weight_factor:
                # resetting the index counter between limb parts
                i = 1.0

    # Creating a hand locator to aim the joints and controls
    hand_loc = cmds.duplicate(pivot_locator_list[-1],
                              name=prefix + 'hand_orient_LOC')[0]
    cmds.parent(hand_loc, pivot_locator_list[-1])
    cmds.setAttr(hand_loc + '.translateX', 2)
    cmds.setAttr(hand_loc + '.localScaleX', 0.5)
    cmds.setAttr(hand_loc + '.localScaleY', 0.5)
    cmds.setAttr(hand_loc + '.localScaleZ', 0.5)
    attr.lock_hide(0, 1, 1, 1, 1, 1, 1, 1, 1, 1, objects=[hand_loc])
    limb_locator_list.append(hand_loc)

    # Creating a locator for the PV position

    # Obtaining the midpoint locator
    pv_setup_loc = cmds.spaceLocator(name='%s_%s_pv_aim_loc'
                                          % (prefix, limb_parts[1]))[0]
    cmds.setAttr(pv_setup_loc + '.overrideEnabled', 1)
    cmds.setAttr(pv_setup_loc + '.overrideDisplayType', 2)
    pv_setup_aim = tool.create_offset(suffix='OFS', input_object=pv_setup_loc)
    # Obtaining the locator at elbow/knee position
    pv_loc = cmds.group(empty=True,
                        name='%s_%s_pv_LOC' % (prefix, limb_parts[1]))
    pv_loc_pivot = tool.create_offset(suffix='OFS', input_object=pv_loc)
    crv.add_curve_shape(shape_choice='arrow', transform_node=pv_loc,
                        color=side_to_color[prefix], shape_offset=[0, 180, 0])
    cmds.xform(pv_loc + '.cv[0:]', scale=[0.5, 0.5, 0.5])
    attr.lock_hide(1, 1, 0, 1, 1, 1, 1, 1, 1, 1, objects=[pv_loc], hide=True)
    cmds.group(pv_loc_pivot, pv_setup_aim, name='%s_%s_pv_GRP'
                                                % (prefix, limb_parts[1]))

    # Constraint setups

    # Aim group at wrist/ankle
    cmds.aimConstraint(pivot_locator_list[-1], pv_setup_aim,
                       maintainOffset=False)
    cmds.pointConstraint(pivot_locator_list[0], pivot_locator_list[-1],
                         pv_setup_aim, maintainOffset=False)
    # Keep the reverse aim locator at the pole point if limb length is variable
    cmds.pointConstraint(pivot_locator_list[1], pv_setup_loc, skip=['y', 'z'])

    # Aim pv back to midpoint
    cmds.pointConstraint(pivot_locator_list[1], pv_loc_pivot,
                         maintainOffset=False)
    cmds.aimConstraint(pv_setup_loc, pv_loc_pivot, maintainOffset=False,
                       aimVector=[0, 0, 1], upVector=[0, 1, 0])
    pv_locator_list.append(pv_loc)

    # Adding the hand locator to the pivot list for the IKFK system after the IK
    # constraint setup is made to not vary the code
    pivot_locator_list.append(hand_loc)


def create_limb_joints(prefix='L', limb_type='arm', auto_twist=True):

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_parts = None
        pass  # Add other_parts to this, but only after other parts are added

    cmds.select(clear=True)
    for loc in limb_locator_list:
        locator_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
        bone = cmds.joint(name=loc.replace('LOC', 'BONE'),
                          position=[locator_position[0],
                          locator_position[1],
                          locator_position[2]])
        limb_bone_list.append(bone)
    # Orient Bones
    cmds.joint(limb_bone_list[0],
               edit=True,
               orientJoint='xzy',
               secondaryAxisOrient='yup',
               children=True)

    # Separating extra joints from pivots to avoid cycles on twists.  Adding
    # x-based point constraints to keep the extra joints from overextending
    # when switching between IKFK.
    pivot_bone_list = []
    for bone in pivot_locator_list:
        pivot_bone_list.append(bone.replace('LOC', 'BONE'))

    bone_parent = None
    if len(limb_dict[limb_parts[0]]) > 1:

        for bone in pivot_bone_list:
            if bone == pivot_bone_list[-1]:
                break
            if bone_parent:
                cmds.parent(bone, bone_parent)
            bone_parent = bone

        i = 0
        j = -1
        bone_count_factor = 1.0 / float(len(limb_dict[limb_parts[0]]))
        bone_position_factor = bone_count_factor
        for bone in limb_bone_list:
            if bone in pivot_bone_list:
                i = i + 1
                j = j + 1
                bone_position_factor = bone_count_factor
                continue
            bone_position_constraint = \
                cmds.pointConstraint(pivot_bone_list[j],
                                     pivot_bone_list[i],
                                     bone,
                                     maintainOffset=False)[0]

            weight_0_attr = cmds.listAttr(bone_position_constraint)[-2]
            weight_1_attr = cmds.listAttr(bone_position_constraint)[-1]

            cmds.setAttr('%s.%s' % (bone_position_constraint, weight_1_attr),
                         bone_position_factor)
            cmds.setAttr('%s.%s' % (bone_position_constraint, weight_0_attr),
                         1 - bone_position_factor)
            bone_position_factor = bone_position_factor + bone_count_factor

    # FK Joint System
    i = 0
    fk_origin = None
    cmds.select(clear=True)
    for loc in pivot_locator_list:
        locator_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
        bone = cmds.joint(name=loc.replace('LOC', 'FK_JNT'),
                          position=[locator_position[0],
                                    locator_position[1],
                                    locator_position[2]])
        if loc == pivot_locator_list[-1]:
            continue
        fk_joints_list.append(bone)
        if i == 0:
            fk_origin = bone
        i = i + 1

    # Orient driver joints
    cmds.joint(fk_joints_list[0],
               edit=True,
               orientJoint='xzy',
               secondaryAxisOrient='yup',
               children=True)

    # IK Joint System
    ik_origin = cmds.duplicate(fk_origin, renameChildren=True)
    ik_joints = name.search_replace_name(search_input='FK',
                                         replace_output='IK',
                                         scope='selection',
                                         input_object=ik_origin)
    for jnt in ik_joints:
        ik_joint_name = name.clear_end_digits(input_object=[jnt])[0]
        ik_joints_list.append(ik_joint_name)
    del(ik_joints_list[-1])

    # FK Controls
    fk_parent = None
    fk_ctrl_list = []
    for ctrl in fk_joints_list:
        if ctrl == fk_joints_list[-1]:
            fk_scnd_control = cmds.group(empty=True,
                                         name=ctrl.replace('JNT', 'SCND_CTRL'))
            fk_scnd_shape = crv.add_curve_shape(shape_choice='ring',
                                                transform_node=fk_scnd_control,
                                                color=side_to_color[prefix],
                                                off_color=True,
                                                shape_offset=[0, 0, 90])
            fk_control = cmds.group(fk_scnd_control,
                                    name=ctrl.replace('JNT', 'CTRL'))
            crv.add_curve_shape(shape_choice='ring',
                                transform_node=fk_control,
                                color=side_to_color[prefix],
                                shape_offset=[0, 0, 90])

            cmds.xform(fk_scnd_control + '.cv[0:]', scale=[1.5, 1.5, 1.5])
            cmds.xform(fk_control + '.cv[0:]', scale=[1.3, 1.3, 1.3])
            attr.lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                           objects=[fk_control, fk_scnd_control])
            attr.create_attr('secondaryVisibility',
                             attribute_type='bool',
                             input_object=fk_control,
                             default_value=0,
                             keyable=False)
            cmds.connectAttr(fk_control + '.secondaryVisibility',
                             fk_scnd_shape + '.v')

            fk_ctrl_list.append(fk_scnd_control)
        else:
            fk_control = cmds.group(empty=True,
                                    name=ctrl.replace('JNT', 'CTRL'))
            crv.add_curve_shape(shape_choice='ring',
                                transform_node=fk_control,
                                color=side_to_color[prefix],
                                shape_offset=[0, 0, 90])

            cmds.xform(fk_control + '.cv[0:]', scale=[1.3, 1.3, 1.3])
            fk_ctrl_list.append(fk_control)
        fk_offset = tool.create_offset(input_object=fk_control)
        tool.match_transformations(source=ctrl, target=fk_offset)
        attr.lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                       objects=[fk_control])
        if limb_parts[0] in fk_offset:
            fk_ctrl_offset.append(fk_offset)
        if fk_parent:
            cmds.parent(fk_offset, fk_parent)

        fk_parent = fk_control

    # IK Controls
    ik_scnd_control = cmds.group(empty=True,
                                 name=ik_joints_list[-1].replace('JNT',
                                                                 'SCND_CTRL'))
    ik_scnd_shape = crv.add_curve_shape(shape_choice='box',
                                        transform_node=ik_scnd_control,
                                        color=side_to_color[prefix],
                                        off_color=True)
    ik_control = cmds.group(ik_scnd_control,
                            name=ik_joints_list[-1].replace('JNT', 'CTRL'))
    crv.add_curve_shape(shape_choice='box',
                        transform_node=ik_control,
                        color=side_to_color[prefix])
    ik_control_offset = tool.create_offset(input_object=ik_control)
    tool.create_offset(suffix='SPACE', input_object=ik_control)

    ik_pv_control = cmds.group(empty=True,
                               name=pv_locator_list[0].replace('LOC', 'CTRL'))
    crv.add_curve_shape(shape_choice='diamond',
                        transform_node=ik_pv_control,
                        color=side_to_color[prefix])
    ik_pv_control_offset = tool.create_offset(input_object=ik_pv_control)
    tool.create_offset(suffix='SPACE', input_object=ik_pv_control)

    cmds.xform(ik_scnd_control + '.cv[0:]', scale=[2.1, 2.1, 2.1])
    cmds.xform(ik_control + '.cv[0:]', scale=[1.85, 1.85, 1.85])

    tool.match_transformations(source=ik_joints_list[-1],
                               target=ik_control_offset)
    tool.match_transformations(source=pv_locator_list[0],
                               target=ik_pv_control_offset)

    ik_ctrl_grp = cmds.group(ik_control_offset, ik_pv_control_offset,
                             name='%s_%s_IK_CTRL_GRP' % (prefix, limb_type))
    ik_ctrl_grp_list.append(ik_ctrl_grp)

    # Deleting the placement pv arrow
    cmds.delete('%s_%s_pv_LOC' % (prefix, limb_parts[1]))

    # Creating FK control constraints
    for ctrl in fk_ctrl_list:
        suffix = 'CTRL'
        if 'SCND' in ctrl:
            suffix = 'SCND_CTRL'
        cmds.parentConstraint(ctrl, ctrl.replace(suffix, 'JNT'))

    ik_handle = cmds.ikHandle(startJoint=ik_joints_list[0],
                              endEffector=ik_joints_list[-1],
                              solver='ikRPsolver',
                              name='%s_%s_IKH' % (prefix, limb_type))[0]
    cmds.poleVectorConstraint(ik_pv_control, ik_handle)
    cmds.parentConstraint(ik_scnd_control, ik_handle)
    cmds.orientConstraint(ik_scnd_control, ik_control.replace('CTRL', 'JNT'))

    # Constraining driver joints to bones
    ikfk_constraint_list = []
    for jnt in range(3):
        ikfk_constraint = cmds.parentConstraint(fk_joints_list[jnt],
                                                ik_joints_list[jnt],
                                                pivot_locator_list[jnt].replace
                                                ('LOC', 'BONE'),
                                                maintainOffset=True)[0]
        ikfk_constraint_list.append(ikfk_constraint)

    # Creating a module node for IKFK passthrough attribute.  Will connect to
    # hand control later, but offers a usable switch now.
    module_node = cmds.group(empty=True, name='%s_%s_MOD' % (prefix, limb_type))
    attr.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, objects=[module_node])
    for attribute in module_attr_list:
        attr.create_attr(attribute,
                         attribute_type=module_attribute_dict[attribute][0],
                         input_object=module_node,
                         min_value=module_attribute_dict[attribute][1],
                         max_value=module_attribute_dict[attribute][2],
                         default_value=module_attribute_dict[attribute][3],
                         keyable=module_attribute_dict[attribute][4],
                         enum_names=module_attribute_dict[attribute][5])

    # Building connection system

    ikfk_rev = node.create_node('REV', name='%s_%s_IKFK' % (prefix, limb_type))
    cmds.connectAttr(module_node + '.IKFK', ikfk_rev + '.inputX')
    for constraint in ikfk_constraint_list:
        weight_0_attr = cmds.listAttr(constraint)[-2]
        weight_1_attr = cmds.listAttr(constraint)[-1]

        cmds.connectAttr(module_node + '.IKFK', '%s.%s'
                         % (constraint, weight_1_attr))
        cmds.connectAttr(ikfk_rev + '.outputX', '%s.%s'
                         % (constraint, weight_0_attr))

    for attribute in ik_end_attr_list:
        attr.create_attr(attribute,
                         attribute_type=ik_end_attribute_dict[attribute][0],
                         input_object=ik_control,
                         min_value=ik_end_attribute_dict[attribute][1],
                         max_value=ik_end_attribute_dict[attribute][2],
                         default_value=ik_end_attribute_dict[attribute][3],
                         keyable=ik_end_attribute_dict[attribute][4],
                         enum_names=ik_end_attribute_dict[attribute][5])

    cmds.connectAttr(ik_control + '.secondaryVisibility', ik_scnd_shape + '.v')
    attr.lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                   objects=[ik_control, ik_scnd_control])
    attr.lock_hide(0, 0, 0, 1, 1, 1, 1, 1, 1, 1, objects=[ik_pv_control])

    if auto_twist and len(limb_dict[limb_parts[0]]) > 1:
        twist_jnt_count = len(limb_dict[limb_parts[1]]) - 1
        twist_jnt_count_fraction = 1.0 / float(len(limb_dict[limb_parts[1]]))
        twist_jnt_index_list = []
        for jnt in range(twist_jnt_count):
            list_jnt = -3 - jnt
            twist_jnt_index_list.append(list_jnt)
        twist_jnt_list = []
        for index in twist_jnt_index_list:
            twist_jnt = limb_bone_list[index]
            twist_jnt_list.append(twist_jnt)

        twist_mdl = node.create_node('MDL', name='%s_%s_twist_factor'
                                                 % (prefix, limb_parts[2]))
        twist_limit_factor_mdl = \
            node.create_node('MDL', name='%s_%s_twist_limit_factor'
                                         % (prefix, limb_parts[2]))
        cmds.connectAttr(limb_bone_list[-2] + '.rotateX',
                         twist_limit_factor_mdl + '.input1')
        cmds.setAttr(twist_limit_factor_mdl + '.input2',
                     twist_jnt_count_fraction)
        cmds.connectAttr(twist_limit_factor_mdl + '.output',
                         twist_mdl + '.input1')
        cmds.connectAttr(module_node + '.foreLimbTwist', twist_mdl + '.input2')
        for bone in twist_jnt_list:
            cmds.connectAttr(twist_mdl + '.output', bone + '.rotateX')


def limb_in_out_module(prefix='L', limb_type='arm'):

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_parts = None
        pass  # Add other_parts to this, but only after other parts are added

    input_node = tool.create_offset(suffix='temp',
                                    input_object=pivot_locator_list[0].replace
                                    ('LOC', 'BONE'))
    output_node = tool.create_child(suffix='temp',
                                    input_object=pivot_locator_list[2].replace
                                    ('LOC', 'BONE'))
    input_module = cmds.rename(input_node, '%s_%s_input_MOD'
                               % (prefix, limb_type))
    output_srt = cmds.rename(output_node, '%s_%s_output_SRT'
                             % (prefix, limb_type))
    output_module = cmds.duplicate(input_module,
                                   name=input_module.replace('input', 'output'),
                                   parentOnly=True)[0]

    output_dcpm = node.create_node('DCPM', name=output_srt)
    cmds.connectAttr(output_srt + '.worldMatrix[0]',
                     output_dcpm + '.inputMatrix')
    cmds.connectAttr(output_dcpm + '.outputTranslate',
                     output_module + '.translate')
    cmds.connectAttr(output_dcpm + '.outputRotate',
                     output_module + '.rotate')
    cmds.connectAttr(output_dcpm + '.outputScale',
                     output_module + '.scale')

    # Putting module parts together
    cmds.parent(input_module, output_module, '%s_%s_MOD' % (prefix, limb_type))
    # Removing setup trash
    cmds.delete(limb_locator_list, '%s_%s_pv_GRP' % (prefix, limb_parts[1]))
    # Putting parts into the input module
    ctrl_grp = cmds.group(ik_ctrl_grp_list, fk_ctrl_offset,
                          name='%s_%s_CTRL_GRP' % (prefix, limb_type))
    jnt_grp = cmds.group(fk_joints_list[0], ik_joints_list[0],
                         name='%s_%s_JNT_GRP' % (prefix, limb_type))
    cmds.group(limb_bone_list[0], name='%s_%s_BONE_GRP' % (prefix, limb_type))
    parts_grp = cmds.group('%s_%s_IKH' % (prefix, limb_type),
                           name='%s_%s_PARTS_GRP' % (prefix, limb_type))
    cmds.parent(ctrl_grp, jnt_grp, parts_grp, input_module)
