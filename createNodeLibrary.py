import maya.cmds as cmds
from functools import partial

node_dictionary = {
    'ADL': partial(cmds.shadingNode, 'addDoubleLinear', asUtility=True),
                   # name='%s_%s' % (name, node_name_dictionary[node_key])),
    'BLC': partial(cmds.shadingNode, 'blendColors', asUtility=True),
    'BTA': partial(cmds.shadingNode, 'blendTwoAttr', asUtility=True),
    'clamp': partial(cmds.shadingNode, 'clamp', asUtility=True),
    'CND': partial(cmds.shadingNode, 'condition', asUtility=True),
    'curveInfo': partial(cmds.shadingNode, 'curveInfo', asUtility=True),
    'DCPM': partial(cmds.shadingNode, 'decomposeMatrix', asUtility=True),
    'DIST': partial(cmds.shadingNode, 'distanceBetween', asUtility=True),
    'MDL': partial(cmds.shadingNode, 'multDoubleLinear', asUtility=True),
    'MDIV': partial(cmds.shadingNode, 'multiplyDivide', asUtility=True),
    'PMA': partial(cmds.shadingNode, 'plusMinusAverage', asUtility=True),
    'REV': partial(cmds.shadingNode, 'reverse', asUtility=True),
    'SR': partial(cmds.shadingNode, 'setRange', asUtility=True),
    'VECP': partial(cmds.shadingNode, 'vectorProduct', asUtility=True)
}

node_name_dictionary = {
    'addDoubleLinear': 'ADL',
    'ADL': 'ADL',
    'blendColors': 'BLC',
    'BLC': 'BLC',
    'blendTwoAttr': 'BTA',
    'BTA': 'BTA',
    'clamp': 'CLMP',
    'CLMP': 'CLMP',
    'condition': 'CND',
    'CND': 'CND',
    'curveInfo': 'curveInfo',
    'decomposeMatrix': 'DCPM',
    'DCPM': 'DCPM',
    'distanceBetween': 'DIST',
    'DIST': 'DIST',
    'multDoubleLinear': 'MDL',
    'MDL': 'MDL',
    'multiplyDivide': 'MDIV',
    'MDIV': 'MDIV',
    'plusMinusAverage': 'PMA',
    'PMA': 'PMA',
    'reverse': 'REV',
    'REV': 'REV',
    'setRange': 'SR',
    'SR': 'SR',
    'vectorProduct': 'VECP',
    'VECP': 'VECP'
}


def create_node(node_key, name=None):
    """
    All useful rigging nodes compacted into one function.  Works the same as

    Args:
        node_key (str): Identity key for node creation.
        name (str): Name for the node.  Node type is automatically added as a
            suffix.

    Returns:
        node_name (str): Name of node for further use.

    """
    if not name:
        name = cmds.ls(selection=True)[0]
    node = node_dictionary[node_name_dictionary[node_key]]()
    node_name = cmds.rename(node,
                            '%s_%s' % (name, node_name_dictionary[node_key]))
    return node_name
