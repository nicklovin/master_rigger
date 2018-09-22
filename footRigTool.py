import maya.cmds as cmds
from string import ascii_uppercase
from MasterRigger import basicTools as tool
from MasterRigger import attributeManipulation as attr
from MasterRigger import curve_assignment as crv
from MasterRigger import createNodeLibrary as node

reverse_foot_parts = ['bank_out', 'bank_in', 'heel', 'toe', 'ball', 'ankle']
toe_library = []

default_vals = [
    [2, 0, 0], [-2, 0, 0], [0, 0, -4], [0, 0, 5], [0, 1, 2], [0, 5, -3]
]

LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}

ROTATE_ORDER = {
    'xyz': 0,
    'yzx': 1,
    'zxy': 2,
    'xzy': 3,
    'yxz': 4,
    'zyx': 5
}

foot_attribute_dict = {
    'secondaryVisibility': ['bool', None, None, 0, False, None],
    'reverseControlVisibility': ['bool', None, None, 0, False, None],
    'toeBend': ['double', None, None, 0, True, None],
    'ballRoll': ['double', None, None, 0, True, None],
    'toeRoll': ['double', None, None, 0, True, None],
    'heelRoll': ['double', None, None, 0, True, None],
    'ballSwivel': ['double', None, None, 0, True, None],
    'toeSwivel': ['double', None, None, 0, True, None],
    'heelSwivel': ['double', None, None, 0, True, None],
    'footBank': ['double', None, None, 0, True, None],
    'twistOffset': ['double', None, None, 0, True, None],
    'upperLengthOffset': ['double', None, None, 0, True, None],
    'lowerLengthOffset': ['double', None, None, 0, True, None]
}
# For calling and filling if toes are created

# List of keys to keep correct order when calling back later
foot_attribute_keys = [
    'secondaryVisibility', 'reverseControlVisibility', 'toeBend', 'ballRoll',
    'toeRoll', 'heelRoll', 'ballSwivel', 'toeSwivel', 'heelSwivel', 'footBank',
    'twistOffset', 'upperLengthOffset', 'lowerLengthOffset'
]

reverse_jnt_list = []

temp_item_list = []

toes_dict = {}


def build_toe_library(toe_count=5, segment_count=1, prefix='C'):
    for toe in range(toe_count):
        toe_letter = LETTERS_INDEX[toe + 1]
        toe_key = '%s_toe%s' % (prefix, toe_letter)
        toe_segment_list = []
        for segment in range(segment_count + 1):
            if segment >= segment_count:
                segment = 'END'
            else:
                segment = str(segment + 1).zfill(2)

            toe_segment_list.append('%s_toe%s_%s'
                                    % (prefix, toe_letter, segment))
        toes_dict[toe_key] = toe_segment_list

    return toes_dict


def create_foot_locators(prefix='C', toes=False, toe_count=5,
                         toe_segments=1):
    rev_orient = None
    parent_joint = None
    toe_temp_parent = None
    i = 0
    for part in reverse_foot_parts:
        if 'bank' in part:
            bank_loc = cmds.spaceLocator(name='%s_%s_rev_LOC' % (prefix, part))
            cmds.setAttr(bank_loc[0] + '.localScaleZ', 5)
            attr.lock_hide(0, 0, 0, 1, 0, 1, 1, 1, 1, 1,
                           objects=[bank_loc[0]])
            cmds.move(default_vals[i][0], default_vals[i][1], default_vals[i][2])
        else:
            cmds.select(clear=True)
            rev_joint = cmds.joint(name='%s_%s_rev_JNT' % (prefix, part))
            if rev_orient:
                cmds.aimConstraint(rev_joint, rev_orient, mo=True,
                                   worldUpType='scene')
            if part == 'ball':
                toe_temp_parent = rev_joint
            rev_orient = cmds.spaceLocator(name='%s_%s_tmp_ROT'
                                                % (prefix, part))[0]
            cmds.setAttr(rev_orient + '.rotateOrder', ROTATE_ORDER['xzy'])
            cmds.pointConstraint(rev_joint, rev_orient, mo=False)
            cmds.joint(rev_joint, edit=True, position=default_vals[i])
            if parent_joint:
                cmds.parent(rev_joint, parent_joint)
            parent_joint = rev_joint
            temp_item_list.append(rev_orient)

        i = i + 1

    if toes:
        build_toe_library(toe_count=toe_count, segment_count=toe_segments,
                          prefix=prefix)
        
        for toe in toes_dict:
            for segment in toes_dict[toe]:
                cmds.spaceLocator(name=segment + '_LOC')
            for loc in range(len(toes_dict[toe])):
                if loc == (len(toes_dict[toe]) - 1):
                    cmds.parent(toes_dict[toe][0] + '_LOC', toe_temp_parent)
                else:
                    cmds.parent(toes_dict[toe][loc + 1] + '_LOC',
                                toes_dict[toe][loc] + '_LOC')

        i = (len(toes_dict) / 2)
        for key in sorted(toes_dict):
            for segment in toes_dict[key]:
                cmds.xform(segment + '_LOC',
                           translation=[0, 0, 1], relative=True)
            cmds.xform(toes_dict[key][0] + '_LOC',
                       translation=[i, 0, 3], relative=True)
            i = i - 1


def create_driver_foot_joints(prefix='C', toes=False, toe_count=5,
                              toe_segments=1):
    loc_parent = None
    for part in reverse_foot_parts:
        if 'bank' in part:
            offset = tool.create_offset(suffix='OFS',
                                        input_object='%s_%s_rev_LOC' %
                                                     (prefix, part))
            if loc_parent:
                cmds.parent(offset, loc_parent)
            attr.lock_hide(1, 1, 1, 1, 1, 0, 1, 1, 1, 1,
                           objects=['%s_%s_rev_LOC' % (prefix, part)])
            loc_parent = '%s_%s_rev_LOC' % (prefix, part)
        else:
            query_loc = '%s_%s_tmp_ROT' % (prefix, part)
            query_jnt = '%s_%s_rev_JNT' % (prefix, part)
            query_parent = cmds.listRelatives(query_jnt, parent=True)
            query_child = cmds.listRelatives(query_jnt, children=True)
            offset = tool.create_offset(suffix='OFS',
                                        input_object=query_jnt)
            if query_parent:
                cmds.parent(offset, world=True)
            if query_child:
                cmds.parent(query_child, world=True)

            cmds.setAttr(query_jnt + '.jointOrientY',
                         cmds.getAttr(query_loc + '.rotateY'))
            if query_parent:
                cmds.parent(offset, query_parent)
            else:
                cmds.parent(offset, loc_parent)
            if query_child:
                cmds.parent(query_child, query_jnt)

            reverse_jnt_list.append(query_jnt)

    # Build the bone system
    start_joint = None
    toe_base_bone = None

    for bone in ['ankle', 'ball', 'toe']:
        cmds.select(clear=True)
        foot_bone = cmds.joint(name='%s_%s_BONE' % (prefix, bone))
        if start_joint:
            cmds.parent(foot_bone, start_joint)
        tool.match_transformations(source='%s_%s_rev_JNT' % (prefix, bone),
                                   target=foot_bone)
        if bone != 'ankle':
            # Looking into matrix based mechanics versus IK
            foot_ik_handle = cmds.ikHandle(startJoint=start_joint,
                                           endEffector=foot_bone,
                                           solver='ikSCsolver',
                                           name='%s_%s_IKH' % (prefix, bone))
            if bone == 'toe':
                cmds.select(clear=True)
                toe_srt = cmds.group(empty=True,
                                     name='%s_%s_bend_SRT' % (prefix, bone))
                tool.match_transformations(target=toe_srt,
                                           source=prefix + '_ball_rev_JNT')
                cmds.parent(foot_ik_handle[0], toe_srt)
                cmds.parent(toe_srt, '%s_%s_rev_JNT' % (prefix, bone))
                toe_base_bone = foot_bone
            else:
                cmds.parent(foot_ik_handle[0], '%s_%s_rev_JNT' % (prefix, bone))
        start_joint = foot_bone
        
    if toes:
        if not toes_dict:
            build_toe_library(toe_count=toe_count, segment_count=toe_segments,
                              prefix=prefix)
        toe_start_list = []
        cmds.select(clear=True)
        # hand_joint replaced by toe_base_bone from above
        for toe in sorted(toes_dict):
            cmds.select(clear=True)
            for segment in toes_dict[toe]:
                locator_position = \
                    cmds.getAttr(segment + '_LOC.worldPosition[0]')[0]
                toe_joint = cmds.joint(name=segment + '_BONE',
                                       position=[locator_position[0],
                                                 locator_position[1],
                                                 locator_position[2]])
                if '01' in segment:
                    toe_start_list.append(toe_joint)

        cmds.parent(toe_start_list, toe_base_bone)

        for toe in sorted(toes_dict):
            for segment in toes_dict[toe]:
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


def build_foot_system(foot_control=None, prefix='C', toes=False,
                      toe_shape_type='box', toe_offset=False, limit_attrs=True):
    # Deleting temp items; might move between different commands or write its
    # own deleting procedure later
    for item in temp_item_list:
        cmds.delete(item)
    # Dealing with the foot control setup
    if not foot_control:
        foot_control = cmds.group(empty=True,
                                  name=prefix + '_foot_IK_CTRL')
        secondary_control = cmds.group(empty=True,
                                       parent=foot_control,
                                       name=prefix + '_foot_IK_SCND_CTRL')
        crv.add_curve_shape('box', foot_control)
        crv.add_curve_shape('square', secondary_control)
        # Match position of ankle
        tool.match_transformations(rotation=False,
                                   source=prefix + '_ankle_rev_JNT',
                                   target=foot_control)
        # Match orientation of heel
        tool.match_transformations(translation=False,
                                   source=prefix + '_heel_rev_JNT',
                                   target=foot_control)
        tool.create_offset(input_object=foot_control)
    else:
        secondary_control = cmds.group(empty=True,
                                       parent=foot_control,
                                       name=prefix + '_foot_IK_SCND_CTRL')
        crv.add_curve_shape('square', secondary_control)
        cmds.xform(secondary_control, translation=[0, 0, 0], relative=True)

    attr.lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                   objects=[foot_control, secondary_control])

    for attribute in foot_attribute_keys:
        attr.create_attr(attribute,
                         attribute_type=foot_attribute_dict[attribute][0],
                         input_object=foot_control,
                         min_value=foot_attribute_dict[attribute][1],
                         max_value=foot_attribute_dict[attribute][2],
                         default_value=foot_attribute_dict[attribute][3],
                         keyable=foot_attribute_dict[attribute][4],
                         enum_names=foot_attribute_dict[attribute][5])

    parent_rev_ctrl = None
    reverse_ctrl_grp = cmds.group(empty=True, name=prefix + '_foot_rev_CTRL_GRP')
    index = 2
    for jnt in reverse_jnt_list:
        if 'ankle' in jnt:
            continue
        rev_control = cmds.group(empty=True, name=jnt.replace('JNT', 'CTRL'))
        crv.add_curve_shape('circle', transform_node=rev_control)
        tool.match_transformations(source=jnt,
                                   target=rev_control)
        rev_offset = tool.create_offset(input_object=rev_control)
        if parent_rev_ctrl:
            cmds.parent(rev_offset, parent_rev_ctrl)
        parent_rev_ctrl = rev_control

        # Node connection network
        reverse_rotate_sum = node.create_node('PMA',
                                              jnt.replace('JNT', 'rotation'))
        cmds.connectAttr(rev_control + '.r', reverse_rotate_sum + '.input3D[0]')
        cmds.connectAttr('%s.%sRoll' % (foot_control, reverse_foot_parts[index]),
                         reverse_rotate_sum + '.input3D[1].input3Dx')
        cmds.connectAttr(
            '%s.%sSwivel' % (foot_control, reverse_foot_parts[index]),
            reverse_rotate_sum + '.input3D[1].input3Dy')
        cmds.connectAttr(reverse_rotate_sum + '.output3D', jnt + '.r')
        if 'heel' in jnt:
            cmds.parent(rev_offset, reverse_ctrl_grp)
            cmds.connectAttr(foot_control + '.reverseControlVisibility',
                             reverse_ctrl_grp + '.v')

        index = index + 1

    foot_roll_cnd = node.create_node('CND', name=prefix + 'footRoll')
    cmds.connectAttr(foot_control + '.footBank',
                     foot_roll_cnd + '.firstTerm')
    cmds.connectAttr(foot_control + '.footBank',
                     foot_roll_cnd + '.colorIfTrueR')
    cmds.connectAttr(foot_control + '.footBank',
                     foot_roll_cnd + '.colorIfFalseG')
    cmds.setAttr(foot_roll_cnd + '.operation', 3)  # Greater than or equal
    cmds.connectAttr(foot_roll_cnd + '.outColor.outColorR',
                     '%s_bank_in_rev_LOC.rz' % prefix)
    cmds.connectAttr(foot_roll_cnd + '.outColor.outColorG',
                     '%s_bank_out_rev_LOC.rz' % prefix)

    # Toe Bend
    cmds.connectAttr(foot_control + '.toeBend', '%s_toe_bend_SRT.rx' % prefix)

    if toes:
        attr_name = []
        toe_ctrl_grp = cmds.group(empty=True, name=prefix + '_toe_CTRL_GRP')
        cmds.parentConstraint(prefix + '_ball_BONE', toe_ctrl_grp, mo=False)
        for toe in sorted(toes_dict):
            # Declaring the parent variable before it gets continually 
            # reassigned
            parent_curve = toe_ctrl_grp
            for segment in toes_dict[toe]:
                if 'END' in segment:
                    continue
                toe_ctrl = cmds.group(empty=True, n=segment + '_CTRL')
                crv.add_curve_shape(shape_choice=toe_shape_type,
                                    transform_node=toe_ctrl)
                toe_srt = cmds.group(toe_ctrl, n=segment + '_SRT')
                if toe_offset:
                    toe_ofs = cmds.group(toe_srt, n=segment + '_OFS')
                    toe_zero = cmds.group(toe_ofs, n=segment + '_ZERO')
                else:
                    toe_zero = cmds.group(toe_srt, n=segment + '_ZERO')

                tool.match_transformations(source=segment + '_BONE',
                                           target=toe_zero)
                cmds.parentConstraint(toe_ctrl, segment + '_BONE')

                # If the control group is not the base of the toe, parent
                if '01' not in segment:
                    cmds.parent(toe_zero, parent_curve)
                    # Lock unnecessary attributes if assigned
                    if limit_attrs:
                        attr.lock_hide(1, 1, 1, 0, 1, 1, 1, 1, 1, 1,
                                       objects=[toe_ctrl])
                else:
                    cmds.parent(toe_zero, toe_ctrl_grp)
                parent_curve = toe_ctrl

                if 'END' not in segment:
                    attr_name.append(segment[2:])

        # Organizer attribute
        attr.create_attr(attribute_name='_', attribute_type='enum',
                         input_object=foot_control, keyable=False,
                         enum_names=['Toes'])
        for attribute in sorted(attr_name):
            attr.create_attr(attribute_name=attribute,
                             attribute_type='double',
                             input_object=foot_control)

            cmds.connectAttr('%s.%s' % (foot_control, attribute),
                             '%s_%s_SRT.rx' % (prefix, attribute))
# Remaining Operations:
# Condition to create a foot control if one does not yet exist
    # Extend this condition to the foot auto rigger in a similar fashion
    # Also extend to find the leg IK handle and put in the reverse hierarchy
    # Original ankle joint will not be influenced otherwise.
