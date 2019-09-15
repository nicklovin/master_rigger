import maya.cmds as cmds
from math import pow, sqrt


def get_selection():
    """
    Returns: The first selected object.
    """
    return cmds.ls(selection=True)[0]


def get_selection_list():
    """
    Returns: List of all selected objects
    """
    return cmds.ls(selection=True)


def get_children(parent):
    """
    Returns: List of children for the input object
    """
    return cmds.listRelatives(parent, children=True)


def get_all_children(parent):
    """
    Returns: A list of all children for an input object
    """
    return cmds.listRelatives(parent, allDescendents=True)


def get_parent(child):
    """
    Returns: The parent of an input object
    """
    return cmds.listRelatives(child, parent=True)


# Check if flag is correct and if this does the correct operation
def get_hierarchy(parent):
    return cmds.listRelatives(parent, allChildren=True)


def get_short_name(longname):
    """
    Returns the shortname of an input object.
    """
    short_name = longname.rsplit('|', 1)[-1]
    return short_name


def get_long_name(name):
    """
    Returns the longname of an object.
    """
    long_name = cmds.ls(name, long=True)[0]
    return long_name


# This might need a keyable flag/variable.  Check after usage
def lock_attr(attribute):
    cmds.setAttr(attribute, lock=True)


def hide_attr(attribute):
    cmds.setAttr(attribute, channelBox=False, keyable=False)


def unlock_attr(attribute):
    cmds.setAttr(attribute, lock=False)


def show_attr(attribute):
    cmds.setAttr(attribute, channelBox=True, keyable=True)


def get_position(obj):
    return cmds.xform(obj, query=True, translation=True, worldSpace=True)


def get_orientation(obj):
    return cmds.xform(obj, query=True, rotation=True, worldSpace=True)


def get_scale(obj):
    return cmds.xform(obj, query=True, scale=True, worldSpace=True)


def get_relative_position(obj):
    return cmds.xform(obj, query=True, translation=True, relative=True)


def get_relative_orientation(obj):
    return cmds.xform(obj, query=True, rotation=True, relative=True)


def get_matrix(obj):
    return cmds.xform(obj, query=True, matrix=True)


def get_world_matrix(obj):
    return cmds.xform(obj, query=True, matrix=True, worldSpace=True)


# Check cmds doc to see if there is a way to do this with xform for consistency
def get_inverse_matrix(obj):
    return cmds.getAttr(obj + '.inverseMatrix')


def get_inverse_world_matrix(obj):
    return cmds.getAttr(obj + '.worldInverseMatrix')


def create_transform(name):
    return cmds.group(empty=True, name=name)


def ensure_list(value):
    if isinstance(value, (list, tuple)):
        return list(value)
    if (value is None):
        return []
    return [value]


def get_distance_between(A, B):
    # If given vectors
    if isinstance(A, (list, tuple)):
        objA = A
        objB = B
    # Else given objects
    else:
        objA = get_position(A)
        objB = get_position(B)

    return sqrt(pow(objA[0] - objB[0], 2) + pow(objA[1] - objB[1], 2) + pow(objA[2] - objB[2], 2))
