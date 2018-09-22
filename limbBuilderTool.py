import maya.cmds as cmds
import pprint  # only for testing purposes, remove when completed
from string import ascii_uppercase
from MasterRigger import curve_assignment as crv
from MasterRigger import basicTools as tool
from MasterRigger import renamerLibrary as name
from MasterRigger import attributeManipulation as attr
reload(name)

print 'test'

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

other_parts = []

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


def create_limb_joints(prefix='L', limb_type='arm', ):

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
        cmds.joint(name=loc.replace('LOC', 'BONE'),
                   position=[locator_position[0],
                             locator_position[1],
                             locator_position[2]])
    # Orient Bones
    cmds.joint(limb_locator_list[0].replace('LOC', 'BONE'),
               edit=True,
               orientJoint='xzy',
               secondaryAxisOrient='yup',
               children=True)

    i = 0
    fk_origin = None
    fk_joints_list = []
    cmds.select(clear=True)
    for loc in pivot_locator_list:
        locator_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
        bone = cmds.joint(name=loc.replace('LOC', 'FK_JNT'),
                          position=[locator_position[0],
                                    locator_position[1],
                                    locator_position[2]])
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

    ik_origin = cmds.duplicate(fk_origin, renameChildren=True)
    ik_joints = name.search_replace_name(search_input='FK',
                                         replace_output='IK',
                                         scope='selection',
                                         input_object=ik_origin)
    ik_joints_list = name.clear_end_digits(input_object=ik_joints)

    # FK Controls
    fk_parent = None
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
        else:
            fk_control = cmds.group(empty=True,
                                    name=ctrl.replace('JNT', 'CTRL'))
            crv.add_curve_shape(shape_choice='ring',
                                transform_node=fk_control,
                                color=side_to_color[prefix],
                                shape_offset=[0, 0, 90])

            cmds.xform(fk_control + '.cv[0:]', scale=[1.3, 1.3, 1.3])
        fk_offset = tool.create_offset(input_object=fk_control)
        tool.match_transformations(source=ctrl, target=fk_offset)
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
    ik_space_ctrl = tool.create_offset(suffix='SPACE', input_object=ik_control)
    ik_control_offset = tool.create_offset(input_object=ik_space_ctrl)

    ik_pv_control = cmds.group(empty=True,
                               name=pv_locator_list[0].replace('LOC', 'CTRL'))
    crv.add_curve_shape(shape_choice='diamond',
                        transform_node=ik_pv_control,
                        color=side_to_color[prefix])
    ik_pv_space_ctrl = tool.create_offset(suffix='SPACE',
                                          input_object=ik_pv_control)
    ik_pv_control_offset = tool.create_offset(input_object=ik_pv_space_ctrl)

    tool.match_transformations(source=ik_joints_list[-1],
                               target=ik_control_offset)
    tool.match_transformations(source=pv_locator_list[0],
                               target=ik_pv_control_offset)

# Build dictionary of limb part names as keys and the in-between joints as a
# list
# Build locators based on all the keys (parts), and groups with handles visible
# for the extra limb joints in reference mode
