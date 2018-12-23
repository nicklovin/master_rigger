import maya.cmds as cmds
import pprint  # only for testing purposes, remove when completed
from string import ascii_uppercase
from master_rigger import curve_assignment as crv
from master_rigger import basicTools as tool
from master_rigger import renamerLibrary as name
from master_rigger import attributeManipulation as attr
from master_rigger import createNodeLibrary as node


LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}

arm_parts = ['shoulder', 'elbow', 'wrist']
leg_parts = ['femur', 'knee', 'ankle']
limb_starting_position = {
    'arm': [3, 17, 0],
    'leg': [2, 9, 0],
    'other': [0, 13, 2]
}

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


def build_limb_library(prefix='L', limb_type='arm', extra_joints=2):
    """
    Building a dictionary variable that holds all of the limb pieces organized
    to be read as needed for the created locators.

    To be utilized properly, this function should be called as a variable and
    used as the limb_dict parameter in all following functions.

    Args:
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.
        limb_type (str): Assign the type of limb to be created.  Expected types
            are 'arm' and 'leg', but if other options are created then the new
            limb will be created using the input string as the identifier.
        extra_joints (int): Assign a number of in-between joints for additional
            influence between the pivot joints of each limb.  If 0, the later
            auto_twist parameter will not be executed regardless of bool state.

    Returns:
        limb_dict (dict): A dictionary of all the limb pivots and the additional
            joints as lists under the keys.  This dictionary will be used for
            all call functions when creating the rig.

    """

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_type = 'other'
        limb_parts = [limb_type + '_01', limb_type + '_02', limb_type + '_03']

    limb_dict = {}
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
    pprint.pprint(limb_dict)
    return limb_dict


def create_limb_locators(limb_dict, prefix='L', limb_type='arm'):
    """
    Building locators for the limbs based on the input limb dictionary.  These
    locators may be manipulated to match the placements of the joints and pivots
    on a body in order to assign the rig.

    Args:
        limb_dict (dict): Assign the dictionary of limb parts to be used for the
            rig building process.
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.
        limb_type (str): Assign the type of limb to be created.  Expected types
            are 'arm' and 'leg', but if other options are created then the new
            limb will be created using the input string as the identifier.

    Returns:
        A list of the following lists/variables needed for the next function.

        limb_locator_list: List of all the locators for the limb.
            Used for bones.
        pivot_locator_list: List of all the pivot points of the limb.
            Used for IKFK joints.
        pv_loc: Object name of the pole vector arrow for placement of the pole.

    """

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_type = 'other'
        limb_parts = [limb_type + '_01', limb_type + '_02', limb_type + '_03']

    pivot_locator_list = []
    limb_locator_list = []
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
                if 'arm' in limb_type:
                    cmds.xform(segment_loc,
                               translation=[distance_factor * i, 0, 0],
                               absolute=True)
                elif 'leg' in limb_type:
                    cmds.xform(segment_loc,
                               translation=[0, distance_factor * -i, 0],
                               absolute=True)
                else:
                    cmds.xform(segment_loc,
                               translation=[0, 0, distance_factor * i],
                               absolute=True)
                i = i + 1
            else:
                cmds.xform(segment_loc,
                           translation=limb_starting_position[limb_type],
                           worldSpace=True)
            # If the locator is the first of the part (key), make its color
            # significant
            if part.endswith(segment):
                crv.set_control_color(rgb_input=side_to_color[prefix],
                                      input_object=segment_loc + 'Shape')
                pivot_locator_list.append(segment_loc)
                parent_loc = segment_loc
                i = 1  # Reset the distance index factor
            else:
                cmds.setAttr(segment_loc + '.localScaleX', 0.5)
                cmds.setAttr(segment_loc + '.localScaleY', 0.5)
                cmds.setAttr(segment_loc + '.localScaleZ', 0.5)
            limb_locator_list.append(segment_loc)

    if 'right' in prefix or 'R' in prefix or 'rt' in prefix:
        for loc in limb_locator_list:
            tx_value = cmds.getAttr(loc + '.translateX')
            cmds.setAttr(loc + '.translateX', -tx_value)

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
                attr.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, objects=[loc])
            elif limb_parts[1] in loc:
                pos_cns = cmds.pointConstraint(pivot_locator_list[1],
                                               pivot_locator_list[2],
                                               loc,
                                               maintainOffset=False)[0]
                cmds.setAttr('%s.%sW0' % (pos_cns, pivot_locator_list[1]),
                             1 - (i / weight_factor))
                cmds.setAttr('%s.%sW1' % (pos_cns, pivot_locator_list[2]),
                             i / weight_factor)
                attr.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, objects=[loc])

            i = i + 1
            if i >= weight_factor:
                # resetting the index counter between limb parts
                i = 1.0

    # Creating a hand locator to aim the joints and controls
    orient_loc = cmds.duplicate(pivot_locator_list[-1],
                                name='%s_%s_orient_LOC'
                                     % (prefix, limb_parts[-1]))[0]
    cmds.setAttr(orient_loc + '.localScaleX', 0.5)
    cmds.setAttr(orient_loc + '.localScaleY', 0.5)
    cmds.setAttr(orient_loc + '.localScaleZ', 0.5)
    if 'arm' in limb_type:
        cmds.parent(orient_loc, pivot_locator_list[-1])
        world_x = cmds.xform(orient_loc, query=True,
                             translation=True,
                             worldSpace=True)[0]
        if world_x > 0:
            cmds.setAttr(orient_loc + '.translateX', 2)
        else:
            cmds.setAttr(orient_loc + '.translateX', -2)
        attr.lock_hide(0, 1, 1, 1, 1, 1, 1, 1, 1, 1, objects=[orient_loc])
    else:
        cmds.parent(orient_loc, world=True)
        ankle_world = node.create_node('DCPM', name='%s_%s_worldY'
                                                    % (prefix, limb_parts[-1]))
        aim_offset = node.create_node('ADL', name='%s_%s_offsetY'
                                                  % (prefix, limb_parts[-1]))
        cmds.connectAttr(pivot_locator_list[-1] + '.worldMatrix[0]',
                         ankle_world + '.inputMatrix')
        cmds.connectAttr(ankle_world + '.outputTranslateY',
                         aim_offset + '.input1')
        cmds.connectAttr(ankle_world + '.outputTranslateX',
                         orient_loc + '.translateX')
        cmds.connectAttr(ankle_world + '.outputTranslateZ',
                         orient_loc + '.translateZ')
        cmds.setAttr(aim_offset + '.input2', -1)
        cmds.connectAttr(aim_offset + '.output', orient_loc + '.translateY')
        attr.lock_hide(0, 0, 0, 1, 1, 1, 1, 1, 1, 1, objects=[orient_loc])
    limb_locator_list.append(orient_loc)

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

    # Adding the hand locator to the pivot list for the IKFK system after the IK
    # constraint setup is made to not vary the code
    pivot_locator_list.append(orient_loc)
    return limb_locator_list, pivot_locator_list, pv_loc


# Work start here.  Must determine what needs to be pushed from the locator
# procedure into the later procedures in order to work with multiple instances.


def create_limb_system(limb_dict, locator_inputs, prefix='L', limb_type='arm',
                       auto_twist=True, orient_symmetry=False, fk_shape='ring',
                       ik_shape='box', pv_shape='diamond'):
    """
    Builds a joint and control rig system based on the placements of the
    locators from the previous function.  Relies heavily on correct variable
    assignments from the returned lists.

    Args:
        limb_dict (dict): Assign the dictionary of limb parts to be used for the
            rig building process.
        locator_inputs (list[list]): Assign the variables created by the return
            values from the previous locator function.
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.
        limb_type (str): Assign the type of limb to be created.  Expected types
            are 'arm' and 'leg', but if other options are created then the new
            limb will be created using the input string as the identifier.
        auto_twist (bool): Assign if the forearm/foreleg twist feature will be
            setup.
        orient_symmetry (bool): Assign the limb to be a oriented as a mirrored
            version of the opposing side.  In a left/right setup, only one side
            should be True.
        fk_shape (str): Assign a shape type for the FK controls.
        ik_shape (str): Assign a shape type for the IK controls.
        pv_shape (str): Assign a shape type for the PV control.

    """

    if limb_type == 'arm':
        limb_parts = arm_parts
    elif limb_type == 'leg':
        limb_parts = leg_parts
    else:
        limb_type = 'other'
        limb_parts = [limb_type + '_01', limb_type + '_02', limb_type + '_03']

    cmds.select(clear=True)
    limb_bone_list = []
    for loc in locator_inputs[0]:
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
    for bone in locator_inputs[1]:
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
    fk_orient_jnt = None
    fk_joints_list = []
    cmds.select(clear=True)
    for loc in locator_inputs[1]:
        locator_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
        bone = cmds.joint(name=loc.replace('LOC', 'FK_JNT'),
                          position=[locator_position[0],
                                    locator_position[1],
                                    locator_position[2]])
        if loc == locator_inputs[1][-1]:
            fk_orient_jnt = loc.replace('_LOC', '_FK_JNT')
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
    ik_joints_list = []
    for jnt in ik_joints:
        ik_joint_name = name.clear_end_digits(input_object=[jnt])[0]
        ik_joints_list.append(ik_joint_name)
    # Deleteing all of the orient joints now that they have been oriented
    cmds.delete(ik_joints_list[-1], limb_bone_list[-1], fk_orient_jnt)
    del(ik_joints_list[-1])

    # Variable to assign the symmetry -1 scale assignment
    inverse = None
    if orient_symmetry:
        inverse = 'y'  # Check if this lines up in all cases

    # FK Controls
    fk_parent = None
    fk_ctrl_offset = []
    fk_ctrl_list = []
    for ctrl in fk_joints_list:
        if ctrl == fk_joints_list[-1]:
            fk_scnd_control = cmds.group(empty=True,
                                         name=ctrl.replace('JNT', 'SCND_CTRL'))
            fk_scnd_shape = crv.add_curve_shape(shape_choice=fk_shape,
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

        fk_offset = tool.create_offset(input_object=fk_control,
                                       invert_scale=inverse)
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
    ik_scnd_shape = crv.add_curve_shape(shape_choice=ik_shape,
                                        transform_node=ik_scnd_control,
                                        color=side_to_color[prefix],
                                        off_color=True)
    ik_control = cmds.group(ik_scnd_control,
                            name=ik_joints_list[-1].replace('JNT', 'CTRL'))
    crv.add_curve_shape(shape_choice=ik_shape,
                        transform_node=ik_control,
                        color=side_to_color[prefix])
    ik_control_offset = tool.create_offset(input_object=ik_control,
                                           invert_scale=inverse)
    ik_space = tool.create_offset(suffix='SPACE', input_object=ik_control)
    cmds.setAttr(ik_space + '.scaleZ', 1)

    ik_pv_control = cmds.group(empty=True,
                               name=locator_inputs[2].replace('LOC', 'CTRL'))
    crv.add_curve_shape(shape_choice=pv_shape,
                        transform_node=ik_pv_control,
                        color=side_to_color[prefix])
    ik_pv_control_offset = tool.create_offset(input_object=ik_pv_control)
    tool.create_offset(suffix='SPACE', input_object=ik_pv_control)

    cmds.xform(ik_scnd_control + '.cv[0:]', scale=[2.1, 2.1, 2.1])
    cmds.xform(ik_control + '.cv[0:]', scale=[1.85, 1.85, 1.85])

    tool.match_transformations(source=ik_joints_list[-1],
                               target=ik_control_offset)
    tool.match_transformations(source=locator_inputs[2],
                               target=ik_pv_control_offset)

    ik_ctrl_grp = cmds.group(ik_control_offset, ik_pv_control_offset,
                             name='%s_%s_IK_CTRL_GRP' % (prefix, limb_type))

    # Deleting the placement pv arrow
    cmds.delete('%s_%s_pv_LOC' % (prefix, limb_parts[1]))

    # Creating FK control constraints
    for ctrl in fk_ctrl_list:
        suffix = 'CTRL'
        if 'SCND' in ctrl:
            suffix = 'SCND_CTRL'
        cmds.parentConstraint(ctrl, ctrl.replace(suffix, 'JNT'),
                              maintainOffset=True)

    ik_handle = cmds.ikHandle(startJoint=ik_joints_list[0],
                              endEffector=ik_joints_list[-1],
                              solver='ikRPsolver',
                              name='%s_%s_IKH' % (prefix, limb_type))[0]
    cmds.poleVectorConstraint(ik_pv_control, ik_handle)
    cmds.parentConstraint(ik_scnd_control, ik_handle, maintainOffset=True)
    cmds.orientConstraint(ik_scnd_control, ik_control.replace('CTRL', 'JNT'))

    # Constraining driver joints to bones
    ikfk_constraint_list = []
    for jnt in range(3):
        ikfk_constraint = cmds.parentConstraint(fk_joints_list[jnt],
                                                ik_joints_list[jnt],
                                                locator_inputs[1][jnt].replace
                                                ('LOC', 'BONE'),
                                                maintainOffset=True)[0]
        ikfk_constraint_list.append(ikfk_constraint)

    # Creating a module node for IKFK pass-through attribute.  Will connect to
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

    cmds.connectAttr(module_node + '.IKFK', ik_ctrl_grp + '.v')
    cmds.connectAttr(ikfk_rev + '.outputX', fk_ctrl_offset[0] + '.v')
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

    # Setting up the module hierarchy.  It make more sense to do this here then
    # use the final function as the connection maker only

    input_node = tool.create_offset(suffix='temp',
                                    input_object=locator_inputs[1][0].replace
                                    ('LOC', 'BONE'))
    output_node = tool.create_child(suffix='temp',
                                    input_object=locator_inputs[1][2].replace
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
    cmds.parent(input_module, output_module,
                '%s_%s_MOD' % (prefix, limb_type))
    # Removing setup trash
    cmds.delete(locator_inputs[0][0], '%s_%s_pv_GRP' % (prefix, limb_parts[1]))
    if cmds.objExists(locator_inputs[0][-1]):
        cmds.delete(locator_inputs[0][-1])

    ctrl_grp = cmds.group(ik_ctrl_grp, fk_ctrl_offset,
                          name='%s_%s_CTRL_GRP' % (prefix, limb_type))
    jnt_grp = cmds.group(fk_joints_list[0], ik_joints_list[0],
                         name='%s_%s_JNT_GRP' % (prefix, limb_type))
    cmds.group(limb_bone_list[0],
               name='%s_%s_BONE_GRP' % (prefix, limb_type))
    parts_grp = cmds.group('%s_%s_IKH' % (prefix, limb_type),
                           name='%s_%s_PARTS_GRP' % (prefix, limb_type))
    cmds.setAttr(parts_grp + '.v', 0)
    cmds.parent(ctrl_grp, jnt_grp, parts_grp, input_module)
