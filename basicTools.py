import maya.cmds as cmds


def create_offset(suffix='ZERO', input_object=None, invert_scale=None):
    """
    Creates an offset transform node for an object.

    Args:
        suffix (str): Assign a suffix name to the offset node.  Default is
            'ZERO', and will automatically change to 'OFS' if a 'ZERO' node is
            selected to allow for multiple levels of offset.
        input_object (str): Assign object to be given the offset node.
        invert_scale (str): Choose an axis to invert with a scale of -1 to allow
            for orientation symmetry.  Expected inputs are x, y, or z.

    Returns:
        offset_node (str): Name of the node for futher use.

    """
    if not input_object:
        input_object = cmds.ls(selection=True)[0]

    sel_parent = cmds.listRelatives(input_object, parent=True)

    if 'ZERO' in input_object:
        suffix = 'OFS'
    offset_node = cmds.group(empty=True, name='%s_%s' % (input_object, suffix))

    object_position = cmds.xform(input_object,
                                 query=True,
                                 translation=True,
                                 worldSpace=True)
    object_orientation = cmds.xform(input_object,
                                    query=True,
                                    rotation=True,
                                    worldSpace=True)

    cmds.setAttr(offset_node + '.tx', object_position[0])
    cmds.setAttr(offset_node + '.ty', object_position[1])
    cmds.setAttr(offset_node + '.tz', object_position[2])
    cmds.setAttr(offset_node + '.rx', object_orientation[0])
    cmds.setAttr(offset_node + '.ry', object_orientation[1])
    cmds.setAttr(offset_node + '.rz', object_orientation[2])

    cmds.parent(input_object, offset_node)

    if invert_scale:
        if invert_scale == 'x':
            cmds.setAttr(offset_node + '.sx', -1)
        elif invert_scale == 'y':
            cmds.setAttr(offset_node + '.sy', -1)
        elif invert_scale == 'z':
            cmds.setAttr(offset_node + '.sz', -1)
        else:
            cmds.warning('Improper input used for inverse_scale parameter!  '
                         'Use "x", "y", or "z".')

    # Put offset node back into hierarchy if one existed
    if sel_parent:
        cmds.parent(offset_node, sel_parent)
    return offset_node


def create_child(suffix='CNS', input_object=None):
    """
    Creates an offset transform node for an object.

    Args:
        suffix (str): Assign a suffix name to the offset node.  Default is
            'ZERO', and will automatically change to 'OFS' if a 'ZERO' node is
            selected to allow for multiple levels of offset.
        input_object (str): Assign object to be given the offset node.

    Returns:
        offset_node (str): Name of the node for futher use.

    """
    if not input_object:
        input_object = cmds.ls(selection=True)[0]

    child_node = cmds.group(empty=True, name='%s_%s' % (input_object, suffix))

    object_position = cmds.xform(input_object,
                                 query=True,
                                 translation=True,
                                 worldSpace=True)
    object_orientation = cmds.xform(input_object,
                                    query=True,
                                    rotation=True,
                                    worldSpace=True)

    cmds.setAttr(child_node + '.tx', object_position[0])
    cmds.setAttr(child_node + '.ty', object_position[1])
    cmds.setAttr(child_node + '.tz', object_position[2])
    cmds.setAttr(child_node + '.rx', object_orientation[0])
    cmds.setAttr(child_node + '.ry', object_orientation[1])
    cmds.setAttr(child_node + '.rz', object_orientation[2])

    cmds.parent(child_node, input_object)

    return child_node


def match_transformations(translation=True, rotation=True, scale=False,
                          source=None, target=None):
    """
    Matches the transformations of a target object to a source object.  Can be
    set to read translation, rotation, and scale.

    Select the target first, then the source.

    Args:
        translation (bool): Query the position of the object.
        rotation (bool): Query the orientation of the object.
        scale (bool): Query the scale of the object.
        selection (bool): Assign function to retrieve source and target from the
            selection.  True by default.
        source (str): Input name of the source object.
        target (str): Input name of the target object.

    """
    if not target:
        target = cmds.ls(selection=True)[0]

    if not source:
        source = cmds.ls(selection=True)[1]

    if translation:
        position = cmds.xform(source, query=True, translation=True,
                              worldSpace=True)
        cmds.xform(target, translation=position, worldSpace=True)
    if rotation:
        orientation = cmds.xform(source, query=True, rotation=True,
                                 worldSpace=True)
        cmds.xform(target, rotation=orientation, worldSpace=True)
    if scale:
        scaling = cmds.xform(source, query=True, scale=True, relative=True)
        cmds.xform(target, scale=scaling, relative=True)
