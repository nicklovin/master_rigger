import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from master_rigger import Splitter
# Force commit comment.

attributes = ['.tx', '.ty', '.tz',
              '.rx', '.ry', '.rz',
              '.sx', '.sy', '.sz',
              '.v']


# TODO: Kwargs?
def lock_hide(tx, ty, tz, rx, ry, rz, sx, sy, sz, v, objects=[], hide=True,
              *args):
    """

    Args:
        tx (int or bool): Assign status of attribute translateX,
            1 or True perform action.
        ty (int or bool): Assign status of attribute translateY,
            1 or True perform action.
        tz (int or bool): Assign status of attribute translateZ,
            1 or True perform action.
        rx (int or bool): Assign status of attribute rotateX,
            1 or True perform action.
        ry (int or bool): Assign status of attribute rotateY,
            1 or True perform action.
        rz (int or bool): Assign status of attribute rotateZ,
            1 or True perform action.
        sx (int or bool): Assign status of attribute scaleX,
            1 or True perform action.
        sy (int or bool): Assign status of attribute scaleY,
            1 or True perform action.
        sz (int or bool): Assign status of attribute scaleZ,
            1 or True perform action.
        v (int or bool): Assign status of attribute visibility,
            1 or True perform action.
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


# TODO: Kwargs: min_value, max_value, default_value, keyable, channelbox, enum_names
# channelbox = kwargs.get('channelbox', True)
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
        input_object = cmds.ls(selection=True, long=True)[0]

    if not input_object:
        raise Exception(
            'No node given! Select or declare object to add attribute to.')

    if type(max_value) is str:
        max_value = None
    if type(min_value) is str:
        min_value = None

    # Checks to see if the attribute already exists (might not be visible)
    if cmds.attributeQuery(attribute_name, node=input_object, exists=True):
        cmds.warning(
                'Attribute already exists on object:"{}".  If not found in the '
                'channelbox, check the Channel Control.'.format(input_object))
        return

    if attribute_type == 'enum':
        enum_list = ''
        for enum in enum_names:
            enum_list = enum_list + enum + ':'
        cmds.addAttr(input_object,
                     longName=attribute_name,
                     attributeType=attribute_type,
                     enumName=enum_list,
                     defaultValue=default_value)
    # Do euler conditions better...
    elif attribute_type == 'euler':
        cmds.addAttr(
            input_object,
            longName=attribute_name,
            attributeType='compound',
            numberOfChildren=3)
        cmds.addAttr(
            input_object,
            longName=attribute_name + 'X',
            attributeType='doubleAngle',
            parent=attribute_name)
        cmds.addAttr(
            input_object,
            longName=attribute_name + 'Y',
            attributeType='doubleAngle',
            parent=attribute_name)

        cmds.addAttr(
            input_object,
            longName=attribute_name + 'Z',
            attributeType='doubleAngle',
            parent=attribute_name)

        for axis in ['X', 'Y', 'Z']:
            cmds.setAttr('%s.%s%s' % (input_object, attribute_name, axis),
                         edit=True,
                         keyable=keyable,
                         channelBox=channelbox)

    else:
        cmds.addAttr(input_object,
                     longName=attribute_name,
                     attributeType=attribute_type,
                     defaultValue=default_value)
    if attribute_type != 'euler':
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
        elif max_value is not None and min_value is None:
            cmds.addAttr('%s.%s' % (input_object, attribute_name),
                         edit=True,
                         max=max_value)

        elif max_value is None and min_value is not None:
            cmds.addAttr('%s.%s' % (input_object, attribute_name),
                         edit=True,
                         min=min_value)


# Wrapper with option to override on locked attributes
def connect_attr(source, target, **kwargs):
    force = kwargs.get('force')
    try:
        cmds.connectAttr(source, target, force=force)
    except Exception as err:
        if kwargs.get('override'):
            sourceLock = cmds.getAttr(source, lock=True)
            targetLock = cmds.getAttr(target, lock=True)
            cmds.setAttr(source, lock=False)
            cmds.setAttr(target, lock=False)
            cmds.connectAttr(source, target, force=force)
            cmds.setAttr(source, lock=sourceLock)
            cmds.setAttr(target, lock=targetLock)
        else:
            raise err


class AttributeWidget(QtWidgets.QFrame):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # Checklist:
        #   - x, y, z checkboxes
        #   - translate, rotate, scale, vis buttons
        #   - custom attribute selection button
        #   - lock/unlock, show/hide dropdowns

        attribute_widget = QtWidgets.QWidget()
        attribute_widget.setLayout(QtWidgets.QVBoxLayout())
        attribute_widget.layout().setContentsMargins(2, 2, 2, 2)
        attribute_widget.layout().setSpacing(5)
        attribute_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                       QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(attribute_widget)

        attribute_button_layout_1 = QtWidgets.QHBoxLayout()
        attribute_button_layout_2 = QtWidgets.QHBoxLayout()
        conditions_layout = QtWidgets.QHBoxLayout()
        lock_unlock_layout = QtWidgets.QHBoxLayout()
        show_hide_layout = QtWidgets.QHBoxLayout()

        attribute_widget.layout().addLayout(attribute_button_layout_1)
        attribute_widget.layout().addLayout(attribute_button_layout_2)
        attribute_widget.layout().addLayout(conditions_layout)
        attribute_widget.layout().addLayout(lock_unlock_layout)
        attribute_widget.layout().addLayout(show_hide_layout)

        translate_button = QtWidgets.QPushButton('Translation')
        rotate_button = QtWidgets.QPushButton('Rotation')
        scale_button = QtWidgets.QPushButton('Scale')
        vis_button = QtWidgets.QPushButton('Vis')
        selected_button = QtWidgets.QPushButton('Selected Attributes')

        attribute_button_layout_1.addWidget(translate_button)
        attribute_button_layout_1.addWidget(rotate_button)
        attribute_button_layout_1.addWidget(scale_button)
        attribute_button_layout_2.addWidget(vis_button)
        attribute_button_layout_2.addWidget(selected_button)

        x_checkbox = QtWidgets.QCheckBox('X')
        y_checkbox = QtWidgets.QCheckBox('Y')
        z_checkbox = QtWidgets.QCheckBox('Z')

        conditions_layout.layout().addWidget(x_checkbox)
        conditions_layout.layout().addWidget(y_checkbox)
        conditions_layout.layout().addWidget(z_checkbox)

        self.lock_case_group = QtWidgets.QButtonGroup()
        self.lock_radio = QtWidgets.QRadioButton('Lock')
        self.unlock_radio = QtWidgets.QRadioButton('Unlock')
        self.lock_case_group.addButton(self.lock_radio)
        self.lock_case_group.addButton(self.unlock_radio)

        condition_divider = QtWidgets.QLabel('|')
        divider_font = QtGui.QFont()
        divider_font.setBold(True)
        condition_divider.setFont(divider_font)
        condition_divider.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        )

        self.hide_case_group = QtWidgets.QButtonGroup()
        self.hide_radio = QtWidgets.QRadioButton('Hide')
        self.show_radio = QtWidgets.QRadioButton('Show')
        self.hide_case_group.addButton(self.hide_radio)
        self.hide_case_group.addButton(self.show_radio)

        self.lock_radio.setChecked(True)
        self.hide_radio.setChecked(True)

        lock_unlock_layout.addWidget(self.lock_radio)
        lock_unlock_layout.addWidget(self.unlock_radio)
        lock_unlock_layout.addWidget(condition_divider)
        lock_unlock_layout.addWidget(self.hide_radio)
        lock_unlock_layout.addWidget(self.show_radio)


class AddAttributesWidget(QtWidgets.QFrame):

    attribute_types_dict = {
        'Angle': 'doubleAngle',
        'Boolean': 'bool',
        'Enum': 'enum',
        'EulerXYZ': 'euler',
        'Float': 'double',
        'FloatXYZ': 'float3',
        'Integer': 'long',
        'Matrix': 'fltMatrix',
        'Spacer': 'enum'
    }

    attribute_types_order = [
        'Float',
        'Integer',
        'Angle',
        'FloatXYZ',
        'EulerXYZ',
        'Boolean',
        'Enum',
        'Matrix',
        'Spacer'
    ]

    enum_index = 0

    enum_index_list = []
    enum_index_layouts = {}

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        add_attribute_widget = QtWidgets.QWidget()
        add_attribute_widget.setLayout(QtWidgets.QVBoxLayout())
        add_attribute_widget.layout().setContentsMargins(2, 2, 2, 2)
        add_attribute_widget.layout().setSpacing(5)
        add_attribute_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(add_attribute_widget)

        # Adding Attributes
        attribute_name_layout = QtWidgets.QHBoxLayout()
        attribute_type_layout = QtWidgets.QHBoxLayout()
        attribute_extras_layout = QtWidgets.QHBoxLayout()
        attribute_enum_layout = QtWidgets.QHBoxLayout()
        attribute_enum_button_layout = QtWidgets.QHBoxLayout()
        attribute_button_layout_3 = QtWidgets.QHBoxLayout()
        attr_reorder_layout = QtWidgets.QHBoxLayout()

        add_attribute_widget.layout().addLayout(attribute_name_layout)
        add_attribute_widget.layout().addLayout(attribute_type_layout)
        add_attribute_widget.layout().addLayout(attribute_extras_layout)
        add_attribute_widget.layout().addLayout(attribute_enum_layout)
        add_attribute_widget.layout().addLayout(attribute_enum_button_layout)
        add_attribute_widget.layout().addLayout(attribute_button_layout_3)
        add_attribute_widget.layout().addLayout(Splitter.SplitterLayout())
        add_attribute_widget.layout().addLayout(attr_reorder_layout)

        create_attr_label = QtWidgets.QLabel('Attribute Name:')
        self.create_attr_line_edit = QtWidgets.QLineEdit('')

        attribute_name_layout.addWidget(create_attr_label)
        attribute_name_layout.addWidget(self.create_attr_line_edit)

        attr_type_label = QtWidgets.QLabel('Attribute Type:')
        self.attr_type_combo = QtWidgets.QComboBox()
        for type in self.attribute_types_order:
            self.attr_type_combo.addItem(type)
        self.attr_type_combo.setFixedWidth(100)

        self.attr_keyable_check = QtWidgets.QCheckBox('Keyable')
        self.attr_keyable_check.setChecked(True)

        attribute_type_layout.addWidget(attr_type_label)
        attribute_type_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        attribute_type_layout.addWidget(self.attr_type_combo)
        attribute_type_layout.addWidget(self.attr_keyable_check)

        min_value_label = QtWidgets.QLabel('Min Value:')
        self.min_value_line_edit = QtWidgets.QLineEdit('')
        max_value_label = QtWidgets.QLabel('Max Value:')
        self.max_value_line_edit = QtWidgets.QLineEdit('')
        default_value_label = QtWidgets.QLabel('Default Value:')
        self.default_value_line_edit = QtWidgets.QLineEdit('0')

        self.min_value_line_edit.setFixedWidth(30)
        self.max_value_line_edit.setFixedWidth(30)
        self.default_value_line_edit.setFixedWidth(30)

        self.min_value_line_edit.setAlignment(QtCore.Qt.AlignRight)
        self.max_value_line_edit.setAlignment(QtCore.Qt.AlignRight)
        self.default_value_line_edit.setAlignment(QtCore.Qt.AlignRight)

        # Integer Validator
        reg_ex = QtCore.QRegExp(r'^(?!@$^_)[0-9\._-]+')
        text_validator = QtGui.QRegExpValidator(reg_ex,
                                                self.min_value_line_edit)
        self.min_value_line_edit.setValidator(text_validator)
        self.max_value_line_edit.setValidator(text_validator)
        self.default_value_line_edit.setValidator(text_validator)

        attribute_extras_layout.addWidget(min_value_label)
        attribute_extras_layout.addWidget(self.min_value_line_edit)
        attribute_extras_layout.addWidget(max_value_label)
        attribute_extras_layout.addWidget(self.max_value_line_edit)
        attribute_extras_layout.addWidget(default_value_label)
        attribute_extras_layout.addWidget(self.default_value_line_edit)

        # Enum Layouts ---------------------------------------------------------
        self.enum_frame = QtWidgets.QFrame()
        self.enum_frame.setStyleSheet('background-color : rgb(27, 28, 30);')
        attribute_enum_layout.layout().addWidget(self.enum_frame)
        self.enum_frame.setLayout(QtWidgets.QVBoxLayout())

        enum_frame_layout = QtWidgets.QHBoxLayout()
        # enum_frame_button_layout = QtWidgets.QHBoxLayout()

        self.enum_frame.layout().addLayout(enum_frame_layout)
        # self.enum_frame.layout().addLayout(enum_frame_button_layout)

        enum_label = QtWidgets.QLabel('Enum Index [0]:')
        enum_index_line_edit = QtWidgets.QLineEdit('')
        enum_index_line_edit.setStyleSheet('background-color : rgb(57, 58, 60);')

        self.enum_index_list.append(enum_index_line_edit)

        enum_frame_layout.addWidget(enum_label)
        enum_frame_layout.addWidget(enum_index_line_edit)

        attribute_enum_button_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        self.enum_clear_index_button = QtWidgets.QPushButton('Clear Enum Indices')
        self.enum_index_button = QtWidgets.QPushButton('Add Enum Index')

        attribute_enum_button_layout.addWidget(self.enum_clear_index_button)
        attribute_enum_button_layout.addWidget(self.enum_index_button)
        self.enum_frame.setVisible(False)
        self.enum_clear_index_button.setVisible(False)
        self.enum_index_button.setVisible(False)

        # Reorder Attributes ---------------------------------------------------

        # For now, use the pre-loaded tool.  Later implement full tool into dock

        attr_reorder_launch_button = QtWidgets.QPushButton('Launch Reorder Attributes')
        attr_reorder_layout.addWidget(attr_reorder_launch_button)

        # ----------------------------------------------------------------------

        attribute_button_layout_3.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        self.create_attr_button = QtWidgets.QPushButton('Create Attribute')
        attribute_button_layout_3.addWidget(self.create_attr_button)

        self.enum_clear_index_button.clicked.connect(self.clear_enum_indices)
        self.enum_index_button.clicked.connect(self.add_enum_index)
        self.create_attr_button.clicked.connect(self._create_attr_parameters)
        self.attr_type_combo.currentIndexChanged.connect(self._adjust_layout_vis)

        attr_reorder_launch_button.clicked.connect(self.launch_reorder_attributes)

    def _create_attr_parameters(self):
        attribute_name = str(self.create_attr_line_edit.text()).strip()

        attribute_type = self.attribute_types_dict[
            self.attr_type_combo.currentText()
        ]

        input_object = cmds.ls(selection=True)
        try:
            min_value = float(self.min_value_line_edit.text())
        except:
            min_value = None
        try:
            max_value = float(self.max_value_line_edit.text())
        except:
            max_value = None
        default_value = float(self.default_value_line_edit.text())
        keyable = self.attr_keyable_check.isChecked()
        visible = True

        enum_names = []
        for item in self.enum_index_list:
            enum_names.append(str(item.text()).strip())

        if self.attr_type_combo.currentText() == 'Spacer':
            enum_names = ['-------']
            keyable = False

        for obj in input_object:
            create_attr(
                attribute_name=attribute_name,
                attribute_type=attribute_type,
                input_object=obj,
                min_value=min_value,
                max_value=max_value,
                default_value=default_value,
                keyable=keyable,
                channelbox=visible,
                enum_names=enum_names
            )

    def add_enum_index(self):
        self.enum_index += 1
        current_index = self.enum_index

        new_enum_index_layout = QtWidgets.QHBoxLayout()
        self.enum_frame.layout().addLayout(new_enum_index_layout)

        self.new_enum_label = QtWidgets.QLabel(
            'Enum Index [%s]:' % str(self.enum_index))
        self.new_enum_line_edit = QtWidgets.QLineEdit('')
        self.new_enum_line_edit.setStyleSheet(
            'background-color : rgb(57, 58, 60);'
        )
        self.new_enum_x_button = QtWidgets.QPushButton('X')
        self.new_enum_x_button.setFixedHeight(20)
        self.new_enum_x_button.setFixedWidth(20)
        self.new_enum_x_button.setStyleSheet(
            'border-radius: 10px;  background-color : rgb(87, 88, 90); font-weight: bold;'
        )

        new_enum_index_layout.addWidget(self.new_enum_label)
        new_enum_index_layout.addWidget(self.new_enum_line_edit)
        new_enum_index_layout.addWidget(self.new_enum_x_button)

        self.enum_index_list.append(self.new_enum_line_edit)
        # self.enum_index_layouts[self.enum_index] =
        self.new_enum_x_button.clicked.connect(
            partial(self.remove_enum_index, new_enum_index_layout, current_index))

    def remove_enum_index(self, layout, index):
        self.clear_layout(layout)
        self.enum_index_list.pop(index)
        # self.enum_index -= 1

    def clear_enum_indices(self):
        if self.enum_index_layouts:
            for layout in self.enum_index_layouts.values():
                self.clear_layout(layout)
        self.enum_index = 0

    def _adjust_layout_vis(self):
        if self.attr_type_combo.currentText() == 'Enum':
            self.enum_frame.setVisible(True)
            self.enum_clear_index_button.setVisible(True)
            self.enum_index_button.setVisible(True)
            self.min_value_line_edit.setEnabled(False)
            self.max_value_line_edit.setEnabled(False)
            # Add stylesheet adjustments when default values added to reverse
            """
            self.min_value_line_edit.setStyleSheet(
                'background-color : rgb(57, 58, 60);')
            self.max_value_line_edit.setStyleSheet(
                'background-color : rgb(57, 58, 60);')
            """
        else:
            self.enum_frame.setVisible(False)
            self.enum_index_button.setVisible(False)
            self.min_value_line_edit.setEnabled(True)
            self.max_value_line_edit.setEnabled(True)

    # Pyside Utility
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def launch_reorder_attributes(self):
        try:
            if 'reorderAttributes' not in globals():
                # import if not already imported
                globals()['reorderAttributes'] = __import__('reorderAttributes')
                reorderAttributes = globals()['reorderAttributes']
                cmds.evalDeferred(reorderAttributes.install)
            else:
                reorderAttributes = globals()['reorderAttributes']
            reorderAttributes.ui.show()
        except IOError:
            raise Exception('PathError(custom): Module not found in path!')
