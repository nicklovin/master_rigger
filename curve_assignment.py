import maya.cmds as cmds
from functools import partial


def control_sphere(*arg):
    circle_1 = cmds.circle(nr=[0, 1, 0], r=1, d=3, ch=0)
    circle_2 = cmds.circle(nr=[1, 0, 0], r=1, d=3, ch=0)
    circle_3 = cmds.circle(nr=[0, 0, 1], r=1, d=3, ch=0)

    cmds.parent(cmds.listRelatives(circle_2, circle_3, shapes=True), circle_1,
                s=True, r=True)
    cmds.delete(circle_2, circle_3)
    return circle_1


curve_library = {
    'circle': partial(cmds.circle,
                      normal=[0, 1, 0],
                      radius=1,
                      degree=3,
                      sections=16,
                      constructionHistory=False),
    'square': partial(cmds.curve,
                      degree=1,
                      point=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]),
    'triangle': partial(cmds.curve,
                        degree=1,
                        point=[(-1, 0, 1), (0, 0, -1), (1, 0, 1)]),
    'octagon': partial(cmds.circle,
                       normal=[0, 1, 0],
                       radius=1,
                       degree=1,
                       sections=8,
                       constructionHistory=False),
    'box': partial(cmds.curve,
                   degree=1,
                   point=[(0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5),
                          (0.5, 0.5, -0.5,), (0.5, 0.5, 0.5,), (0.5, -0.5, 0.5,),
                          (0.5, -0.5, -0.5,), (0.5, 0.5, -0.5,),
                          (-0.5, 0.5, -0.5,), (-0.5, -0.5, -0.5,),
                          (-0.5, -0.5, 0.5,), (-0.5, 0.5, 0.5,),
                          (-0.5, -0.5, 0.5,), (0.5, -0.5, 0.5,),
                          (0.5, -0.5, -0.5,), (-0.5, -0.5, -0.5,)]),
    'sphere': control_sphere,
    'pyramid': partial(cmds.curve,
                       degree=1,
                       point=[(9.27258e-008, -0.353553, -0.707107), (-0.707107,
                              -0.353553, -6.18172e-008), (0, 0.353553, 0),
                              (9.27258e-008, -0.353553, -0.707107), (0.707107,
                              -0.353553, 0), (0, 0.353553, 0), (-3.09086e-008,
                              -0.353553, 0.707107), (0.707107, -0.353553, 0),
                              (-3.09086e-008, -0.353553, 0.707107), (-0.707107,
                              -0.353553, -6.18172e-008)]),
    'diamond': partial(cmds.curve,
                       degree=1,
                       point=[(0, 1, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0),
                              (0, 0, -1), (-1, 0, 0), (0, 1, 0), (0, 0, 1),
                              (-1, 0, 0), (0, -1, 0), (0, 0, 1), (1, 0, 0),
                              (0, -1, 0), (0, 0, -1), (1, 0, 0)]),
    'quad_arrow': partial(cmds.curve,
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

    'arrow': partial(cmds.curve,
                     degree=1,
                     p=[(0, 0, 0), (2, 0, 2), (1, 0, 2), (1, 0, 3), (1, 0, 4),
                        (1, 0, 5), (1, 0, 6), (1, 0, 7), (1, 0, 8), (0, 0, 8),
                        (-1, 0, 8), (-1, 0, 7), (-1, 0, 6), (-1, 0, 5),
                        (-1, 0, 4), (-1, 0, 3), (-1, 0, 2), (-2, 0, 2)]),
    'plus': partial(cmds.curve,
                    degree=1,
                    p=[(-1, 0, -1), (-1, 0, -3), (1, 0, -3), (1, 0, -1),
                       (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3),
                       (-1, 0, 3), (-1, 0, 1), (-3, 0, 1), (-3, 0, -1)]),
    'ring': partial(cmds.curve,
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
                       -0.1, 0.707107)])
}

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
    'ring': True
}

rgb_dictionary = {
    'red': [1, 0, 0],
    'pink': [1, .25, .25],
    'orange': [1, .2, 0],
    'yellow': [1, 1, 0],
    'green': [0, 1, 0],
    'cyan': [0, 1, 1],
    'blue': [0, 0, 1],
    'magenta': [1, 0, 1],
    'purple': [1, 0, 1],
    'white': [1, 1, 1],
    'grey': [.6, .6, .6]
}
# Index colors are blown out by comparison, so these values are more correct
rgb_actuals = {
    'red': [8.509607315063477, -0.010916219092905521, -0.010916219092905521],
    'pink': [8.509607315063477, 0.5029946565628052, 0.5029946565628052],
    'orange': [(1.270400047302246, 0.33289995789527893, -0.010800041258335114)],
    'yellow': [8.509607315063477, 8.509607315063477, -0.010916219092905521],
    'green': [-0.010916219092905521, 8.509607315063477, -0.010916219092905521],
    'cyan': [0.14030349254608154, 1.1826233863830566, 8.509607315063477],
    'blue': [-0.010916219092905521, -0.010916219092905521, 8.509607315063477],
    'magenta': [0.770842432975769, -0.010916443541646004, 0.770842432975769],
    'purple': [0.770842432975769, -0.010916443541646004, 0.770842432975769],
    'white': [8.509607315063477, 8.509607315063477, 8.509607315063477],
    'grey': [.9, .9, .9]
}


def set_control_color(rgb_input, input_object=None):
    """
    Sets an override color value to an object or shape node for the purpose of
    distinctions of controls in a rig.

    Args:
        rgb_input (str) or (list[float, float, float]): Assigns a color value to
            set for a shape node.  If string, it must be compatible with the
            keys in rgb_dictionary.  If list, it must have 3 float values that
            correspond with the desired color values in range 0 to 1.
        input_object (str): Object/Shape name that is being affected.  Shape
            nodes will perform best.

    """
    if not input_object:
        input_object = cmds.ls(selection=True)[0]
    # setting the color value based on the passed argument
    if type(rgb_input) is list:
        if len(rgb_input) != 3:
            cmds.warning('Color value input list is not the proper size!  '
                         'Input 3 floats between 0 and 1 to assign a color.')
            return
        rgb = rgb_input
    elif rgb_input in rgb_actuals:
        rgb = rgb_actuals[rgb_input]
    else:
        # This condition will only work when called directly, never when called
        # from the add_curve_shape function
        rgb = cmds.colorEditor(query=True, rgb=True)

    if type(input_object) is list:
        for shape in input_object:
            cmds.setAttr(shape + '.overrideEnabled', 1)
            cmds.setAttr(shape + '.overrideRGBColors', 1)
            cmds.setAttr(shape + '.overrideColorR', rgb[0])
            cmds.setAttr(shape + '.overrideColorG', rgb[1])
            cmds.setAttr(shape + '.overrideColorB', rgb[2])
    else:
        cmds.setAttr(input_object + '.overrideEnabled', 1)
        cmds.setAttr(input_object + '.overrideRGBColors', 1)
        cmds.setAttr(input_object + '.overrideColorR', rgb[0])
        cmds.setAttr(input_object + '.overrideColorG', rgb[1])
        cmds.setAttr(input_object + '.overrideColorB', rgb[2])


def add_curve_shape(shape_choice, transform_node=None, color=None,
                    off_color=False, shape_offset=False):
    """
    Creates a shape node that is input into a transform node.  This will turn a
    transform node into a control shape, allowing for more flexibility in
    building rigging systems that want interchangeable control shape types.
    Shapes may also be assigned a color, to add more distinct appearance.

    Args:
        shape_choice (str): Assigns the shape type for the control.  Availble
            shapes are in the dictionaries listed in the function file.
        transform_node (str): Assigns the transform node that will receive the
            shape node (converting it into a control).  If no input is given,
            will default to the selection.
        color (str) or (list[float, float, float]): Assigns a color value to set
            for the new curve shape.  If string, it must be compatible with the
            keys in rgb_dictionary.  If list, it must have 3 float values that
            correspond with the desired color values in range 0 to 1.
        off_color (bool): If color parameter is a string, all the values in the
            corresponding value list will be cut in half to provide a similar,
            but different color result.  If color parameter is not a string,
            then parameter is benign.
        shape_offset (list[float, float, float]): Assign rotation values for the
            shape to offset its visual direction.  Will have no effect on the
            transform values, only visual feedback of the shape.

    """
    # curve library calling
    if not transform_node:
        transform_node = cmds.ls(selection=True)[0]

    if not transform_node:
        cmds.warning('No input given for the transform_node! Please select an '
                     'object or input a parameter.')
        return

    curve_transform = curve_library[shape_choice]()
    curve_shape = cmds.listRelatives(curve_transform, shapes=True)
    if curve_library_bool[shape_choice]:
        cmds.closeCurve(curve_shape, ch=0, replaceOriginal=1)
    cmds.parent(curve_shape, transform_node, shape=True, r=True)
    cmds.delete(curve_transform)

    # Curve color operations
    if color:
        if color in rgb_dictionary:
            # If an off-color variation is desired, change values to half
            if off_color:
                curve_color = [float(c) / 1.5 for c in rgb_dictionary[color]]
                # Color is a string name used as a key
            else:
                curve_color = rgb_actuals[color]
            set_control_color(rgb_input=curve_color)
        elif type(color) is list:
            # Color is a list of 3 float values
            set_control_color(rgb_input=color)
        else:
            # Neither condition met, no action may be performed
            cmds.warning('Input for "color" parameter is not an acceptable '
                         'value.  Please input one of the appropriate strings '
                         'mentioned in the "help" function, or input a color '
                         'value list like so: [float, float, float].')
            return

    if shape_offset:
        cmds.xform(transform_node + '.cv[0:]', rotation=shape_offset)

    shape_name = cmds.rename(curve_shape, transform_node + 'Shape')
    return shape_name


def normalize_ctrl_scale(input_object=None):
    """
    Set a consistent and readable scale for a control shape's size without
    requiring the user to access component mode or touch the curve CVs.  Set the
    scale of a control, then execute to have the control maintain size without
    affecting other objects or freezing the transformations.

    Scaling some controls may break the rig temporarily, but running the
    procedure will reset the positions.

    Args:
        input_object (str) or (list[str]): The control objects/shapes that need
            to be affected.

    """
    if not input_object:
        input_object = cmds.ls(selection=True)
    if input_object is list and len(input_object) > 1:
        for ctrl in input_object:
            ctrl_scale = cmds.xform(ctrl, query=True, scale=True, relative=True)
            cmds.xform(ctrl, scale=[1, 1, 1])
            cmds.xform(ctrl + '.cv[0:]', scale=ctrl_scale)
    else:
        ctrl_scale = cmds.xform(input_object,
                                query=True,
                                scale=True,
                                relative=True)
        cmds.xform(input_object, scale=[1, 1, 1])
        cmds.xform(input_object + '.cv[0:]', scale=ctrl_scale)
