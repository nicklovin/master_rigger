import maya.cmds as cmds


attributes = ['.tx', '.ty', '.tz',
              '.rx', '.ry', '.rz',
              '.sx', '.sy', '.sz',
              '.v']


def lock_hide(tx, ty, tz, rx, ry, rz, sx, sy, sz, v, objects=[], hide=True,
              *args):
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
        objects (list[str]): Assign object(s) to have attributes affected.
            Only works if selection=False.
        hide (bool): Assign if function should hide the locked attribute.
        *args (list[str]): Add any additional attributes to lock/hide.
            Should be entered as '.attribute_name'

    """
    if not objects:
        objects = cmds.ls(selection=True)

    # Check if hiding should be done on top of locking
    if hide:
        attr_keyable = False
    else:
        attr_keyable = True

    for obj in objects:
        a = 0
        attr_type = [tx, ty, tz, rx, ry, rz, sx, sy, sz, v]
        for attr in attributes:
            if attr_type[a] == 0 or False:
                cmds.setAttr(obj + attr, lock=False, keyable=True)
            else:
                cmds.setAttr(obj + attr, lock=True, keyable=attr_keyable)
            a = a + 1

        # if additional arguments are passed, they are assumed to be locked
        if args:
            for attr in args:
                cmds.setAttr(obj + attr, lock=True, keyable=attr_keyable)


def create_attr(attribute_name, attribute_type, input_object=None,
                min_value=None, max_value=None, default_value=0, keyable=True,
                channelbox=True, enum_names=[]):
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
        channelbox (bool): If keyable is set to False, this parameter is checked
            to see if the attribute should remain visible while non-keyable.
        enum_names (list[str]): Sets the name values for enum attributes.  Will
            not passed if attribute_type is not 'enum'.

    """
    # Checks to make sure an object is passed for the attribute
    if not input_object:
        input_object = cmds.ls(selection=True)[0]

    if not input_object:
        cmds.warning('Could not find an object to add to!  Please select or '
                     'declare object to add attribute to.')
        return

    # Checks to see if the attribute already exists (might not be visible)
    if not cmds.attributeQuery(attribute_name, node=input_object, exists=True):
        if attribute_type == 'enum':
            enum_list = ''
            for enum in enum_names:
                enum_list = enum_list + enum + ':'
            cmds.addAttr(input_object,
                         longName=attribute_name,
                         attributeType=attribute_type,
                         enumName=enum_list,
                         defaultValue=default_value)
        else:
            cmds.addAttr(input_object,
                         longName=attribute_name,
                         attributeType=attribute_type,
                         defaultValue=default_value)
    if keyable:
        cmds.setAttr('%s.%s' % (input_object, attribute_name),
                     edit=True,
                     keyable=keyable)
    else:
        cmds.setAttr('%s.%s' % (input_object, attribute_name),
                     edit=True,
                     keyable=keyable,
                     channelBox=channelbox)

    # If value is a number, check for min/max values
    if 'float' or 'double' or 'int' or 'long' in attribute_type:
        if max_value is not None and min_value is not None:
            cmds.addAttr('%s.%s' % (input_object, attribute_name),
                         edit=True,
                         max=max_value,
                         min=min_value)
    # If only one min/max argument is passed, return a warning
        elif (max_value is None and min_value is not None) or \
             (min_value is None and max_value is not None):
            cmds.warning('Max and Min values will only be applied if both '
                         'arguments have values.')
