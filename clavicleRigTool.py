import maya.cmds as cmds
from master_rigger import renamerLibrary as name
from master_rigger import curve_assignment as crv
from master_rigger import basicTools as tool

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

    base_loc = cmds.spaceLocator(name=prefix + '_clav_LOC',
                                 position=clav_starting_position[0])[0]
    end_loc = cmds.spaceLocator(name=prefix + '_clav_END_LOC',
                                position=clav_starting_position[1])[0]

    clav_locator_list = [base_loc, end_loc]

    cmds.parent(end_loc, base_loc)

    return clav_locator_list


def build_clav_system(locator_inputs, prefix='L', orient_symmetry=False,
                      fk_shape='ring', ik_shape='plus'):

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
