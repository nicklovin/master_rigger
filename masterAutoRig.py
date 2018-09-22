import pymel.core as pm
import maya.mel as mel
import types
from functools import partial


# Global variables, lists, and dictionaries
attributes = ['.tx', '.ty', '.tz',
              '.rx', '.ry', '.rz',
              '.sx', '.sy', '.sz',
              '.v']

body_parts_dictionary = {
    'spine': ['pelvis', 'spine', 'chest'],
    'neck': ['neck'],
    'head': ['head', 'jaw', 'eye'],
    'arm': ['shoulder', 'elbow', 'wrist'],
    'clavicle': ['clav'],
    'hand': ['thumb', 'index', 'middle', 'ring', 'pinky'],
    'leg': ['hip', 'knee', 'ankle'],
    'foot': ['heel', 'ball', 'toe']
}
# need to re-evaluated as world spaces (currently object/parent spaces)
skeleton_base_values = {
    'ankle': [0, -4.0, -1.0],
    'chest': [0, 4.0, 0.0],
    'clav': [1.0, 17.0, 1.0],
    'elbow': [3.0, -3.0, -1.0],
    'eye': [0.5, 21.0, 1.0],
    'head': [0.0, 2.0, 0.0],
    'hip': [1.5, 9.0, 0.0],
    'knee': [0.0, -4.0, 1.0],
    'neck': [0.0, 19.0, 0.0],
    'pelvis': [0.0, 10.0, 0.0],
    'shoulder': [2.5, 17.5, 0.0],
    'spine': [0, 3.5, 0.0],
    'toe': [0.0, -1.0, 2.0],
    'wrist': [2.0, -3.0, 1.0]
}

# colors + values
rgb_dictionary = {
    'red': [1, 0, 0],
    'orange': [1, .4, 0],
    'yellow': [1, 1, 0],
    'green': [0, 1, 0],
    'cyan': [0, 1, 1],
    'blue': [0, 0, 1],
    'magenta': [1, 0, 1],
    'purple': [1, 0, 1],
    'white': [1, 1, 1],
}

# Multi-shaped controls (require separate definitions)


def control_sphere(*arg):
    circle_1 = pm.circle(nr=[0, 1, 0], r=1, d=3, ch=0)
    circle_2 = pm.circle(nr=[1, 0, 0], r=1, d=3, ch=0)
    circle_3 = pm.circle(nr=[0, 0, 1], r=1, d=3, ch=0)

    pm.parent(pm.listRelatives(circle_2, circle_3, shapes=True), circle_1,
              s=True, r=True)
    pm.delete(circle_2, circle_3)
    return circle_1


# Curve point dictionary that creates curve shape node to be put into a
# transform control node.  This make it easier to allow curve choices later.
curve_library = {
    'circle': partial(pm.circle,
                      normal=[0, 1, 0],
                      radius=1,
                      degree=3,
                      sections=16,
                      constructionHistory=False),
    'square': partial(pm.curve,
                      degree=1,
                      point=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]),
    'triangle': partial(pm.curve,
                        degree=1,
                        point=[(-1, 0, 1), (0, 0, -1), (1, 0, 1)]),
    'octagon': partial(pm.circle,
                       normal=[0, 1, 0],
                       radius=1,
                       degree=1,
                       sections=8,
                       constructionhistory=False),
    'box': partial(pm.curve,
                   degree=1,
                   point=[(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5),
                          (0.5, 0.5, -0.5,), (0.5, 0.5, 0.5,),
                          (0.5, -0.5, 0.5,),
                          (0.5, -0.5, -0.5,), (0.5, 0.5, -0.5,),
                          (-0.5, 0.5, -0.5,), (-0.5, -0.5, -0.5,),
                          (-0.5, -0.5, 0.5,), (-0.5, 0.5, 0.5,),
                          (-0.5, -0.5, 0.5,), (0.5, -0.5, 0.5,),
                          (0.5, -0.5, -0.5,), (-0.5, -0.5, -0.5,)]),
    'sphere': control_sphere,
    'pyramid': partial(pm.curve,
                       degree=1,
                       point=[(9.27258e-008, -0.353553, -0.707107), (-0.707107,
                              -0.353553, -6.18172e-008), (0, 0.353553, 0),
                              (9.27258e-008, -0.353553, -0.707107), (0.707107,
                              -0.353553, 0), (0, 0.353553, 0), (-3.09086e-008,
                              -0.353553, 0.707107), (0.707107, -0.353553, 0),
                              (-3.09086e-008, -0.353553, 0.707107), (-0.707107,
                              -0.353553, -6.18172e-008)]),
    'diamond': partial(pm.curve,
                       degree=1,
                       point=[(0, 1, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0),
                              (0, 0, -1), (-1, 0, 0), (0, 1, 0), (0, 0, 1),
                              (-1, 0, 0), (0, -1, 0), (0, 0, 1), (1, 0, 0),
                              (0, -1, 0), (0, 0, -1), (1, 0, 0)]),
    'quad_arrow': partial(pm.curve,
                          degree=1,
                          p=[(0.4, 0.0, -0.4), (0.4, 0.0, -0.6),
                              (0.4, 0.0, -0.8), (0.4, 0.0, -1.0),
                              (0.4, 0.0, -1.2), (0.8, 0.0, -1.2),
                              (0.6, 0.0, -1.4), (0.4, 0.0, -1.6),
                              (0.2, 0.0, -1.8), (0.0, 0.0, -2.0),
                              (-0.2, 0.0, -1.8), (-0.4, 0.0, -1.6),
                              (-0.6, 0.0, -1.4), (-0.8, 0.0, -1.2),
                              (-0.4, 0.0, -1.2), (-0.4, 0.0, -1.0),
                              (-0.4, 0.0, -0.8), (-0.4, 0.0, -0.6),
                              (-0.4, 0.0, -0.4), (-0.6, 0.0, -0.4),
                              (-0.8, 0.0, -0.4), (-1.0, 0.0, -0.4),
                              (-1.2, 0.0, -0.4), (-1.2, 0.0, -0.6),
                              (-1.2, 0.0, -0.8), (-1.4, 0.0, -0.6),
                              (-1.6, 0.0, -0.4), (-1.8, 0.0, -0.2),
                              (-2.0, 0.0, 0.0),
                              (-1.8, 0.0, 0.2), (-1.6, 0.0, 0.4),
                              (-1.4, 0.0, 0.6), (-1.2, 0.0, 0.8),
                              (-1.2, 0.0, 0.4), (-1.0, 0.0, 0.4),
                              (-0.8, 0.0, 0.4), (-0.6, 0.0, 0.4),
                              (-0.4, 0.0, 0.4), (-0.4, 0.0, 0.6),
                              (-0.4, 0.0, 0.8), (-0.4, 0.0, 1.0),
                              (-0.4, 0.0, 1.2), (-0.8, 0.0, 1.2),
                              (-0.6, 0.0, 1.4), (-0.4, 0.0, 1.6),
                              (-0.2, 0.0, 1.8), (0.0, 0.0, 2.0),
                              (0.2, 0.0, 1.8), (0.4, 0.0, 1.6),
                              (0.6, 0.0, 1.4), (0.8, 0.0, 1.2), (0.4, 0.0, 1.2),
                              (0.4, 0.0, 1.0), (0.4, 0.0, 0.8), (0.4, 0.0, 0.6),
                              (0.4, 0.0, 0.4), (0.6, 0.0, 0.4), (0.8, 0.0, 0.4),
                              (1.0, 0.0, 0.4), (1.2, 0.0, 0.4), (1.2, 0.0, 0.8),
                              (1.4, 0.0, 0.6), (1.6, 0.0, 0.4), (1.8, 0.0, 0.2),
                              (2.0, 0.0, 0.0),
                              (1.8, 0.0, -0.2), (1.6, 0.0, -0.4),
                              (1.4, 0.0, -0.6), (1.2, 0.0, -0.8),
                              (1.2, 0.0, -0.6), (1.2, 0.0, -0.4),
                              (1.0, 0.0, -0.4), (0.8, 0.0, -0.4),
                              (0.6, 0.0, -0.4)]),

    'arrow': partial(pm.curve,
                     degree=1,
                     p=[(-1, 0, -3), (-1, 0, -3), (-1, 0, -3), (-2, 0, -3),
                        (-2, 0, -3), (-2, 0, -3), (-2, 0, -3), (0, 0, -5),
                        (0, 0, -5), (0, 0, -5), (0, 0, -5), (2, 0, -3),
                        (2, 0, -3), (2, 0, -3), (2, 0, -3), (1, 0, -3),
                        (1, 0, -3), (1, 0, -3), (1, 0, -3), (1, 0, -2),
                        (1, 0, -1), (1, 0, 0), (1, 0, 1), (1, 0, 2),
                        (1, 0, 3), (1, 0, 3), (1, 0, 3), (1, 0, 3),
                        (-1, 0, 3), (-1, 0, 3), (-1, 0, 3), (-1, 0, 3),
                        (-1, 0, 2), (-1, 0, 1), (-1, 0, 0), (-1, 0, -1),
                        (-1, 0, -2)]),
    'plus': partial(pm.curve,
                    degree=1,
                    p=[(-1, 0, -1), (-1, 0, -3), (1, 0, -3), (1, 0, -1),
                       (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3),
                       (-1, 0, 3), (-1, 0, 1), (-3, 0, 1), (-3, 0, -1)]),
    'ring': partial(pm.curve,
                    d=1,
                    p=[(0.707107, 0.1, 0.707107), (1, 0.1, 0), (1, -0.1, 0),
                       (0.707107, -0.1, -0.707107), (0.707107, 0.1,
                       -0.707107), (0, 0.1, -1), (0, -0.1, -1), (-0.707107,
                       -0.1, -0.707107), (-0.707107, 0.1, -0.707107), (-1,
                       0.1, 0), (-1, -0.1, 0), (-0.707107, -0.1, 0.707107),
                       (-0.707107, 0.1, 0.707107), (0, 0.1, 1), (0, -0.1, 1),
                       (0.707107, -0.1, 0.707107), (0.707107, 0.1, 0.707107),
                       (0, 0.1, 1), (0, -0.1, 1), (-0.707107, -0.1,
                       0.707107), (-0.707107, 0.1, 0.707107), (-1, 0.1, 0),
                       (-1, -0.1, 0), (-0.707107, -0.1, -0.707107),
                       (-0.707107, 0.1, -0.707107), (0, 0.1, -1), (0, -0.1,
                       -1), (0.707107, -0.1, -0.707107), (0.707107, 0.1,
                       -0.707107), (1, 0.1, 0), (1, -0.1, 0), (0.707107,
                       -0.1, 0.707107)]),
    'locator': partial(pm.spaceLocator)

}
# Related to the above dictionary, this helps reduce the CVs created
curve_library_bool = {
    'circle': False,
    'square': True,
    'triangle': True,
    'octagon': False,
    'box': False,
    'sphere': False,
    'pyramid': False,  # might be True
    'diamond': False,  # might be True
    'quad_arrow': True,
    'arrow': True,
    'plus': True,
    'ring': True,
    'locator': False
}


# Command to add a shape node to an object, allowing controllers to be created
# as transform nodes and let the user choose a shape preference
def add_curve_shape(shape_choice, transform_node=None, color=''):
    # curve library calling
    if not transform_node:
        transform_node = pm.ls(selection=True)[0]

    curve_transform = curve_library[shape_choice]()
    curve_shape = pm.listRelatives(curve_transform, shapes=True)[0]
    if curve_library_bool[shape_choice]:
        pm.closeCurve(curve_shape, ch=0, replaceOriginal=1)
    if color:
        set_color(color, input_shape=curve_shape)
    pm.parent(curve_shape, transform_node, shape=True, r=True)
    pm.rename(curve_shape, transform_node + '_Shape')
    pm.delete(curve_transform)


# Node library for easier calling
node_dictionary = {
    'ADL': partial(pm.shadingNode, 'addDoubleLinear', asUtility=True),
    'BLC': partial(pm.shadingNode, 'blendColors', asUtility=True),
    'BTA': partial(pm.shadingNode, 'blendTwoAttr', asUtility=True),
    'clamp': partial(pm.shadingNode, 'clamp', asUtility=True),
    'CND': partial(pm.shadingNode, 'condition', asUtility=True),
    'curveInfo': partial(pm.shadingNode, 'curveInfo', asUtility=True),
    'DCMX': partial(pm.shadingNode, 'decomposeMatrix', asUtility=True),
    'DIST': partial(pm.shadingNode, 'distanceBetween', asUtility=True),
    'MDL': partial(pm.shadingNode, 'multDoubleLinear', asUtility=True),
    'MDIV': partial(pm.shadingNode, 'multiplyDivide', asUtility=True),
    'PMA': partial(pm.shadingNode, 'plusMinusAverage', asUtility=True),
    'REV': partial(pm.shadingNode, 'reverse', asUtility=True),
    'SR': partial(pm.shadingNode, 'setRange', asUtility=True),
    'VECP': partial(pm.shadingNode, 'vectorProduct', asUtility=True)
}
# Allow for short or long name inputs in the calling function
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
    'decomposeMatrix': 'DCMX',
    'DCMX': 'DCMX',
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
    the shadingNode command, but requires less flags and cleanly names the
    nodes.
    Args:
        node_key (str): Node type to create, can be long or short name.
        name (str): Assign name to the node.  Automatically adds the node type
            as a suffix.

    Returns:
        Returns the node that was just created for calling.

    """
    if not name:
        name = pm.ls(selection=True)[0]
    node = node_dictionary[node_name_dictionary[node_key]]()
    pm.rename(node, '%s_%s' % (name, node_name_dictionary[node_key]))
    return node


def lock_hide(tx, ty, tz, rx, ry, rz, sx, sy, sz, v, hide=True, *args):
    """

    Args:
        tx (int or bool): Assign status of attribute translateX,
            0 or False perform action.
        ty (int or bool): Assign status of attribute translateY,
            0 or False perform action.
        tz (int or bool): Assign status of attribute translateZ,
            0 or False perform action.
        rx (int or bool): Assign status of attribute rotateX,
            0 or False perform action.
        ry (int or bool): Assign status of attribute rotateY,
            0 or False perform action.
        rz (int or bool): Assign status of attribute rotateZ,
            0 or False perform action.
        sx (int or bool): Assign status of attribute scaleX,
            0 or False perform action.
        sy (int or bool): Assign status of attribute scaleY,
            0 or False perform action.
        sz (int or bool): Assign status of attribute scaleZ,
            0 or False perform action.
        v (int or bool): Assign status of attribute visibility,
            0 or False perform action.
        hide (bool): Assign if function should hide the locked attribute.
        *args (list[str]): Add any additional attributes to lock/hide.
            Should be entered as '.attribute_name'
    """
    # Check if hiding should be done on top of locking
    if hide:
        attr_keyable = False
    else:
        attr_keyable = True

    a = 0
    attr_type = [tx, ty, tz, rx, ry, rz, sx, sy, sz, v]
    for attr in attributes:
        if attr_type[a] == 0 or False:
            pm.setAttr(attr, lock=False, keyable=True)
        else:
            pm.setAttr(attr, lock=True, keyable=attr_keyable)
        a = a + 1

    # if additional arguments are passed, they are assumed to be locked
    if args:
        for attr in args:
            pm.setAttr(attr, lock=True, keyable=attr_keyable)


def create_attr(attribute_name, attribute_type, input_object=None,
                min_value=None, max_value=None, default_value=0, keyable=True,
                enum_names=[]):
    """

    Args:
        attribute_name (str): The long name of the attribute to add.
        attribute_type (str): The type of attribute to add.
        input_object (str): Object that will have the attribute added.  If none
            provided, the first selection will be used.
        min_value (int): Sets a minimum value.  Only works if passed with a max
            value.
        max_value (int): Sets a maximum value.  Only works if passed with a min
            value.
        default_value (float/int): Sets a default value.  If not provided,
            default will default to 0.
        keyable (bool): Sets the attribute to be keyable.  Defaults to True.
        enum_names (list[str]): Sets the name values for enum attributes.  Will
            not passed if attribute_type is not 'enum'.

    Returns:

    """
    # Checks to make sure an object is passed for the attribute
    if not input_object:
        input_object = pm.ls(selection=True)[0]

    if not input_object:
        pm.warning('Could not find an object to add to!  Please select or '
                   'declare object to add attribute to.')
        return

    # Checks to see if the attribute already exists (might not be visible)
    if not pm.attributeQuery(attribute_name, node=input_object, exists=True):
        if attribute_type == 'enum':
            enum_list = ''
            for enum in enum_names:
                enum_list = enum_list + enum + ':'
            pm.addAttr(input_object,
                       longName=attribute_name,
                       attributeType=attribute_type,
                       enumName=enum_list,
                       defaultValue=default_value)
        else:
            pm.addAttr(input_object,
                       longName=attribute_name,
                       attributeType=attribute_type,
                       defaultValue=default_value)
    pm.setAttr('%s.%s' % (input_object, attribute_name),
               edit=True,
               keyable=keyable)

    # If value is a number, check for min/max values
    if 'float' or 'double' or 'int' or 'long' in attribute_type:
        if max_value is not None and min_value is not None:
            pm.addAttr('%s.%s' % (input_object, attribute_name),
                       edit=True,
                       max=max_value,
                       min=min_value)
    # If only one min/max argument is passed, return a warning
        elif (max_value is None and min_value is not None) or \
             (min_value is None and max_value is not None):
            pm.warning('Max and Min values will only be applied if both '
                       'arguments have values.')


def set_color(rgb_input, selection=False, input_shape=''):
    # setting the color value based on the passed argument
    if selection:
        input_shape = pm.ls(sl=True)[0]

    if rgb_input in rgb_dictionary:
        rgb = rgb_dictionary[rgb_input]
    else:
        rgb = pm.colorEditor(query=True, rgb=True)

    pm.setAttr(input_shape + '.overrideEnabled', 1)
    pm.setAttr(input_shape + '.overrideRGBColors', 1)
    pm.setAttr(input_shape + '.overrideColorR', rgb[0])
    pm.setAttr(input_shape + '.overrideColorG', rgb[1])
    pm.setAttr(input_shape + '.overrideColorB', rgb[2])


def simple_rig_setup(rig_name):  # input as needed
    ctrl_setup_names = ['Global', 'Local']
    hierarchy_names = ['GLOBAL_MOVE', 'IK', 'CTRL', 'JNT', 'BONE', 'DRIVER',
                       'GEO', 'PROXY', 'RENDER', 'SPACE', 'MISC_NODES',
                       'PLACEMENT', 'SCRIPT_NODES', 'DEFORMER',
                       'DEFORMER_HANDLE', 'NONSCALE_JNTS', 'BLENDSHAPES']
    group_names = []

    local_master = pm.group(em=True, n=ctrl_setup_names[1] + '_CTRL')
    add_curve_shape('circle')
    set_color('yellow')
    global_master = pm.group(em=True, n=ctrl_setup_names[0] + '_CTRL')
    add_curve_shape('quad_arrow')
    set_color('yellow')
    rig = pm.group(em=True, n=rig_name)

    for g in hierarchy_names:
        grp = pm.group(em=True, n=g + '_GRP')
        group_names.append(grp)
        pm.parent(grp, rig)

    # global move grp
    pm.parent(group_names[1], group_names[2], group_names[3], group_names[0])
    # joint type grp
    pm.parent(group_names[4], group_names[5], group_names[3])
    # geo type grp
    pm.parent(group_names[7], group_names[8], group_names[6])
    # spaces under local
    pm.parent(group_names[9], local_master)
    # deformer type grp
    pm.parent(group_names[-1], group_names[-2], group_names[-3],
              group_names[-4])
    # local under global
    pm.parent(local_master, global_master)
    # global under placement
    pm.parent(global_master, group_names[11])
    # connecting global move parts to the matrix of the master controllers
    global_matrix = pm.shadingNode('decomposeMatrix',
                                   asUtility=True,
                                   name='global_DCMX')
    pm.connectAttr(local_master + '.worldMatrix[0]',
                   global_matrix + '.inputMatrix')
    pm.connectAttr(global_matrix + '.outputTranslate',
                   group_names[0] + '.translate')
    pm.connectAttr(global_matrix + '.outputRotate',
                   group_names[0] + '.rotate')
    pm.connectAttr(global_matrix + '.outputScale', group_names[0] + '.scale')
    # set geo grp to reference by default
    pm.setAttr(group_names[6] + '.overrideEnabled', 1)
    pm.setAttr(group_names[6] + '.overrideDisplayType', 2)

    # add attrs to global and local + set connections
    pm.addAttr(local_master, ln='localScale', at='double', dv=1)
    pm.setAttr(local_master + '.localScale', keyable=True)
    for s in ['X', 'Y', 'Z']:
        pm.connectAttr(local_master + '.localScale',
                       local_master + '.scale' + s)
    pm.select(local_master)
    lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1)

    pm.addAttr(global_master, ln='globalScale', at='double', dv=1)
    pm.addAttr(global_master, ln='_', nn=' ', at='enum', en='GEO:')
    pm.addAttr(global_master, ln='geoVis', at='enum', en='Proxy:Render:',
               dv=1)
    pm.setAttr(global_master + '.globalScale', keyable=True)
    pm.setAttr(global_master + '._', keyable=False, lock=True, cb=True)
    pm.setAttr(global_master + '.geoVis', keyable=False, cb=True)
    for s in ['X', 'Y', 'Z']:
        pm.connectAttr(global_master + '.globalScale',
                       global_master + '.scale' + s)
    pm.select(global_master)
    lock_hide(0, 0, 0, 0, 0, 0, 1, 1, 1, 1)
    return global_master, local_master


def setup_positions():

    for key in body_parts_dictionary:
        print key
        component_setter = body_parts_dictionary[key]
        if key == 'foot' or key == 'hand':
            continue
        if isinstance(component_setter, types.StringTypes):
            component_position = skeleton_base_values[component_setter]
            pm.joint(n=component_setter, position=component_position)
            mel.eval('jointOrientToggleAxesVisibility')
            add_curve_shape('locator', color='yellow')
            pm.select(cl=True)
        else:
            for component in component_setter:
                if component == 'jaw':
                    continue
                component_position = skeleton_base_values[component]
                pm.joint(n=component, position=component_position)
                mel.eval('jointOrientToggleAxesVisibility')
                add_curve_shape('locator', color='yellow')
                pm.select(cl=True)
