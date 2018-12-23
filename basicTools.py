import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import renamerLibrary as lib


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

    if not input_object:
        cmds.group(empty=True, name='null_%s' % suffix)
        return

    sel_parent = cmds.listRelatives(input_object, parent=True)

    if 'ZERO' in input_object:
        suffix = 'OFS'
    obj_short_name = lib.split_long_names(input_object)
    offset_node = cmds.group(empty=True, name='%s_%s' % (obj_short_name, suffix))

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

    if not input_object:
        cmds.group(empty=True, name='null_%s' % suffix)
        return

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


class OffsetNodeWidget(QtWidgets.QFrame):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        offsets_widget = QtWidgets.QWidget()
        offsets_widget.setLayout(QtWidgets.QVBoxLayout())
        offsets_widget.layout().setContentsMargins(2, 2, 2, 2)
        offsets_widget.layout().setSpacing(5)
        offsets_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(offsets_widget)

        buttons_layout = QtWidgets.QHBoxLayout()
        override_layout = QtWidgets.QHBoxLayout()

        offsets_widget.layout().addLayout(buttons_layout)
        offsets_widget.layout().addLayout(override_layout)

        create_offset_button = QtWidgets.QPushButton('Create Offset')
        create_child_button = QtWidgets.QPushButton('Create Child')

        buttons_layout.addWidget(create_offset_button)
        buttons_layout.addWidget(create_child_button)

        self.override_checkbox = QtWidgets.QCheckBox('Override Suffix')
        self.override_checkbox.setChecked(False)
        self.override_line_edit = QtWidgets.QLineEdit('')
        self.override_line_edit.setPlaceholderText('ZERO')
        self.override_line_edit.setStyleSheet(
            'background-color : rgb(57, 58, 60);')
        self.override_line_edit.setEnabled(False)

        override_layout.addWidget(self.override_checkbox)
        override_layout.addWidget(self.override_line_edit)

        create_offset_button.clicked.connect(self.run_create_offset)
        create_child_button.clicked.connect(self.run_create_child)

        self.override_checkbox.stateChanged.connect(self._update_override_enable)

    def _update_override_enable(self):
        value = self.override_checkbox.checkState()
        self.override_line_edit.setEnabled(value)
        if value:
            self.override_line_edit.setStyleSheet(
                'background-color : rgb(37, 38, 40);'
            )
        else:
            self.override_line_edit.setStyleSheet(
                'background-color : rgb(57, 58, 60);'
            )

    def _get_suffix_parameter(self):
        new_suffix = str(self.override_line_edit.text()).strip()
        return new_suffix

    def run_create_offset(self):
        if self.override_checkbox.checkState():
            suffix = self._get_suffix_parameter()
            create_offset(suffix=suffix)
        else:
            create_offset()

    def run_create_child(self):
        if self.override_checkbox.checkState():
            suffix = self._get_suffix_parameter()
            create_child(suffix=suffix)
        else:
            create_child()


class TransformWidget(QtWidgets.QFrame):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        transform_widget = QtWidgets.QWidget()
        transform_widget.setLayout(QtWidgets.QVBoxLayout())
        transform_widget.layout().setContentsMargins(2, 2, 2, 2)
        transform_widget.layout().setSpacing(5)
        transform_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                       QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(transform_widget)

        instruction_layout = QtWidgets.QHBoxLayout()
        button_layout_1 = QtWidgets.QHBoxLayout()
        button_layout_2 = QtWidgets.QHBoxLayout()

        transform_widget.layout().addLayout(instruction_layout)
        transform_widget.layout().addLayout(button_layout_1)
        transform_widget.layout().addLayout(button_layout_2)

        instructions = QtWidgets.QLabel(
            'Select the target object, then the source.'
        )
        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        instruction_layout.addWidget(instructions)
        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        transform_button = QtWidgets.QPushButton('Match Transformations')
        button_layout_1.addWidget(transform_button)

        translation_button = QtWidgets.QPushButton('Translations')
        rotation_button = QtWidgets.QPushButton('Rotation')
        scale_button = QtWidgets.QPushButton('Scale')
        button_layout_2.addWidget(translation_button)
        button_layout_2.addWidget(rotation_button)
        button_layout_2.addWidget(scale_button)

        transform_button.clicked.connect(
            partial(match_transformations, True, True, True))
        translation_button.clicked.connect(
            partial(match_transformations, True, False, False))
        rotation_button.clicked.connect(
            partial(match_transformations, False, True, False))
        scale_button.clicked.connect(
            partial(match_transformations, False, False, True))
