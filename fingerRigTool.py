import maya.cmds as cmds
from string import ascii_uppercase
from master_rigger import curve_assignment as crv
from master_rigger import attributeManipulation as attr
from master_rigger import createNodeLibrary as node

# Letters for finger enumeration
LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}
# Dictionary variable, used for all callbacks and built with first function
fingers_dict = {}
# control variable may not be necessary depending on input requests for window
hand_control = None


def build_hand_module():
    pass


def build_finger_library(finger_count=4, thumb=True, segment_count=3,
                         prefix='C'):
    """
    Builds a dictionary (library) of all the parts of the hand/fingers based on
    the inputs to suit individualized characters not limited to human hand
    features.

    Args:
        finger_count (int): The number of fingers being created, thumb excluded.
        thumb (bool): If building a thumb is needed.
        segment_count (int): the number of finger segments in each finger.
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.

    Returns:
        fingers_dict (dictionary): Dictionary with each finger as a key, giving
            a list for the segments of the given finger key.

    """

    for finger in range(finger_count):
        finger = finger + 1
        finger_letter = LETTERS_INDEX[finger]
        finger_key = '%s_finger%s' % (prefix, finger_letter)
        finger_segment_list = []
        for segment in range(segment_count + 1):
            if segment >= segment_count:
                segment = 'END'
            else:
                segment = str(segment + 1).zfill(2)

            finger_segment_list.append('%s_finger%s_%s'
                                       % (prefix, finger_letter, segment))
        fingers_dict[finger_key] = finger_segment_list

    if thumb:
        thumb_segment_list = []
        thumb_key = prefix + '_thumb'
        for segment in range(segment_count + 1):
            if segment >= segment_count:
                segment = 'END'
            else:
                segment = str(segment + 1).zfill(2)

            thumb_segment_list.append('%s_thumb_%s'
                                      % (prefix, segment))
        fingers_dict[thumb_key] = thumb_segment_list

    return fingers_dict


def create_finger_locators(prefix='C'):
    """
    Creates the locators for the finger position alignments.

    Args:
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.

    """
    hand_parent = cmds.spaceLocator(name=prefix + '_hand_LOC')[0]
    for finger in fingers_dict:
        for segment in fingers_dict[finger]:
            cmds.spaceLocator(name=segment + '_LOC')
        for loc in range(len(fingers_dict[finger])):
            if loc == (len(fingers_dict[finger]) - 1):
                cmds.parent(fingers_dict[finger][0] + '_LOC', hand_parent)
            else:
                cmds.parent(fingers_dict[finger][loc + 1] + '_LOC',
                            fingers_dict[finger][loc] + '_LOC')

    cmds.setAttr(hand_parent + '.overrideEnabled', 1)
    cmds.setAttr(hand_parent + '.overrideColor', 13)

    i = (len(fingers_dict)/2) - 1
    for key in sorted(fingers_dict):
        for segment in fingers_dict[key]:
            cmds.move(1, 0, 0, segment + '_LOC', relative=True)
        cmds.move(1, 0, i, fingers_dict[key][0] + '_LOC', relative=True)
        if key == (prefix + '_thumb'):
            cmds.rotate(0, -45, 0, fingers_dict[key][0] + '_LOC', relative=True)
            cmds.move(-1, 0, len(fingers_dict), fingers_dict[key][0] + '_LOC',
                      relative=True)
        i = i - 1


def create_finger_joints(prefix='C'):
    """
    Creates the joints for the finger.

    Args:
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.

    """
    finger_start_list = []
    cmds.select(clear=True)
    hand_joint = cmds.joint(name=prefix + '_hand_BONE')
    for finger in sorted(fingers_dict):
        cmds.select(clear=True)
        for segment in fingers_dict[finger]:
            locator_position = cmds.getAttr(segment + '_LOC.worldPosition[0]')[0]
            finger_joint = cmds.joint(name=segment + '_BONE',
                                      position=[locator_position[0],
                                                locator_position[1],
                                                locator_position[2]])
            if '01' in segment:
                finger_start_list.append(finger_joint)

    cmds.parent(finger_start_list, hand_joint)

    for finger in sorted(fingers_dict):
        for segment in fingers_dict[finger]:
            locator_reference = segment + '_LOC'
            joint_reference = segment + '_BONE'
            locator_position = cmds.getAttr(locator_reference
                                            + '.worldPosition[0]')[0]
            locator_rotations = cmds.getAttr(locator_reference + '.r')[0]
            cmds.setAttr(joint_reference + '.jointOrientX',
                         locator_rotations[0])
            cmds.setAttr(joint_reference + '.jointOrientY',
                         locator_rotations[1])
            cmds.setAttr(joint_reference + '.jointOrientZ',
                         locator_rotations[2])
            cmds.joint(joint_reference,
                       edit=True,
                       position=[locator_position[0],
                                 locator_position[1],
                                 locator_position[2]])


def create_finger_controls(shape_type='box', offset=False, limit_attrs=False,
                           hand_ctrl=True, prefix='C', hand_shape='triangle'):
    """
    Creates controls for the joints of the finger.

    Args:
        shape_type (str): Assigns the control shape type for the individual
            finger controls.  Options vary based on the curve_assignment
            availability (must be imported properly to function).
        offset (bool): Allow for an additional offset group to be added to the
            control chain (can be used for gimbal, set-driven keys, etc.)
        limit_attrs (bool): Automatically lock attributes on segments, limiting
            controls to rotateZ.
        hand_ctrl (bool): Create a single control to override/blend with the
            individual controls on the finger.  By default, will also contain
            attributes for IKFK and other useful tools.  True by default.
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.

    """
    attr_name = []

    for finger in sorted(fingers_dict):
        # Declaring the parent variable before it gets continually reassigned
        parent_curve = None
        for segment in fingers_dict[finger]:
            if 'END' in segment:
                continue
            finger_ctrl = cmds.group(empty=True, n=segment + '_CTRL')
            crv.add_curve_shape(shape_choice=shape_type,
                                transform_node=finger_ctrl)
            finger_srt = cmds.group(finger_ctrl, n=segment + '_SRT')
            if offset:
                finger_ofs = cmds.group(finger_srt, n=segment + '_OFS')
                finger_zero = cmds.group(finger_ofs, n=segment + '_ZERO')
            else:
                finger_zero = cmds.group(finger_srt, n=segment + '_ZERO')
            segment_position = cmds.xform(segment + '_BONE',
                                          query=True,
                                          translation=True,
                                          worldSpace=True)
            segment_orientation = cmds.xform(segment + '_BONE',
                                             query=True,
                                             rotation=True,
                                             worldSpace=True)
            cmds.setAttr(finger_zero + '.tx', segment_position[0])
            cmds.setAttr(finger_zero + '.ty', segment_position[1])
            cmds.setAttr(finger_zero + '.tz', segment_position[2])
            cmds.setAttr(finger_zero + '.rx', segment_orientation[0])
            cmds.setAttr(finger_zero + '.ry', segment_orientation[1])
            cmds.setAttr(finger_zero + '.rz', segment_orientation[2])

            # If the control group is not the base of the finger, parent
            if '01' not in segment:
                cmds.parent(finger_zero, parent_curve)
                # Lock unnecessary attributes if assigned
                if limit_attrs:
                    attr.lock_hide(1, 1, 1, 1, 1, 0, 1, 1, 1, 1,
                                   objects=[finger_ctrl])
            parent_curve = finger_ctrl

            if 'END' not in segment:
                attr_name.append(segment[2:])
    
    if hand_ctrl:
        hand_control = cmds.group(empty=True, name=prefix + '_hand_CTRL')
        crv.add_curve_shape(shape_choice=hand_shape,
                            transform_node=hand_control)
        hand_position = cmds.xform(hand_control.replace('CTRL', 'BONE'),
                                   query=True,
                                   translation=True,
                                   worldSpace=True)
        hand_orientation = cmds.xform(hand_control.replace('CTRL', 'BONE'),
                                      query=True,
                                      rotation=True,
                                      worldSpace=True)

        cmds.setAttr(hand_control + '.tx', hand_position[0])
        cmds.setAttr(hand_control + '.ty', hand_position[1])
        cmds.setAttr(hand_control + '.tz', hand_position[2])
        cmds.setAttr(hand_control + '.rx', hand_orientation[0])
        cmds.setAttr(hand_control + '.ry', hand_orientation[1])
        cmds.setAttr(hand_control + '.rz', hand_orientation[2])
        
        attr.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                       objects=[hand_control])
        
        attr.create_attr(attribute_name='IKFK',
                         attribute_type='double',
                         input_object=hand_control,
                         min_value=0, max_value=1, default_value=1)
        attr.create_attr(attribute_name='spread',
                         attribute_type='double',
                         input_object=hand_control,
                         min_value=-10, max_value=10)
        attr.create_attr(attribute_name='masterRotation',
                         attribute_type='double',
                         input_object=hand_control)
        attr.create_attr(attribute_name='offset',
                         attribute_type='double',
                         input_object=hand_control)
        attr.create_attr(attribute_name='offsetFavor',
                         attribute_type='enum',
                         input_object=hand_control, default_value=1,
                         enum_names=['Inner', 'Outer'])

        for attribute in sorted(attr_name):
            attr.create_attr(attribute_name=attribute,
                             attribute_type='double',
                             input_object=hand_control)

        for key in sorted(fingers_dict):
            vis_attribute = key[len(prefix) + 1:] + '_Vis'
            attr.create_attr(attribute_name=vis_attribute,
                             attribute_type='bool',
                             input_object=hand_control, default_value=1)

        return hand_control


def connect_fingers(hand_ctrl=hand_control, prefix='C'):
    """
    Creates necessary connections for the fingers, and applies them to the hand
    control if applicable.

    Args:
        hand_ctrl (str): Assign name of the hand control created in the previous
            step.  If used with interface, should be automatically assigned.  If
            using commands separately, set manually.
        prefix (str): Body orientation of the fingers.
            'LCR' are appropriate inputs.

    """
    # Declaring early repeating factors
    offset_attr_factor = 0
    reverse_attr_factor = len(fingers_dict) - 2  # accounts for no thumb offset

    for finger in sorted(fingers_dict):
        # Building the node network
        if hand_ctrl:
            # Visibility connections
            cmds.connectAttr('%s.%s_Vis' % (hand_ctrl, finger[len(prefix) + 1:]),
                             finger + '_01_ZERO.v')
            # Remove the thumb from the automations
            if 'thumb' not in finger:
                finger_srt_mult = node.create_node('MDIV', name=finger)
                finger_srt_cnd = node.create_node('CND', name=finger)

                cmds.setAttr(finger_srt_cnd + '.colorIfFalseR',
                             reverse_attr_factor)
                cmds.setAttr(finger_srt_cnd + '.colorIfTrueR',
                             offset_attr_factor)
                cmds.setAttr(finger_srt_cnd + '.secondTerm', 0)
                cmds.setAttr(finger_srt_cnd + '.operation', 1)

                cmds.connectAttr(finger_srt_cnd + '.outColorR',
                                 finger_srt_mult + '.input2X')
                cmds.connectAttr(hand_ctrl + '.offsetFavor',
                                 finger_srt_cnd + '.firstTerm')
                cmds.connectAttr(hand_ctrl + '.offset',
                                 finger_srt_mult + '.input1X')

        # Creating the initial segment constraints
        for segment in fingers_dict[finger]:
            if 'END' in segment:
                continue
            ctrl = segment + '_CTRL'
            bone = segment + '_BONE'
            cmds.parentConstraint(ctrl, bone, mo=True)

            # Building the SRT values network, if applicable
            if hand_ctrl:
                finger_attr = segment[len(prefix) + 1:]
                finger_srt_sum = node.create_node('PMA', name=segment)
                if 'thumb' in segment:
                    cmds.connectAttr(hand_ctrl + '.' + finger_attr,
                                     segment + '_SRT.rz')
                else:
                    cmds.connectAttr(hand_ctrl + '.masterRotation',
                                     finger_srt_sum + '.input1D[0]')
                    cmds.connectAttr(finger_srt_mult + '.outputX',
                                     finger_srt_sum + '.input1D[1]')
                    cmds.connectAttr(hand_ctrl + '.' + finger_attr,
                                     finger_srt_sum + '.input1D[2]')
                    cmds.connectAttr(finger_srt_sum + '.output1D',
                                     segment + '_SRT.rz')

        offset_attr_factor = offset_attr_factor + 1
        reverse_attr_factor = reverse_attr_factor - 1
