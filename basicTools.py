import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from maya_tools import mayaFrameWidget
import renamerLibrary as lib

from master_rigger import cmdsTranslator as nUtil
reload(nUtil)

DEFAULT_PANEL = 'modelPanel4'


def create_null(name='null', suffix='NULL'):
    return cmds.createNode('transform', name='{}_{}'.format(name, suffix))


def create_pivot(name=None):
    clst = cmds.cluster()
    cmds.select(cl=True)
    jnt = cmds.joint(name=name or 'pivotJoint1')
    cmds.parentConstraint(clst, jnt, maintainOffset=False)
    cmds.delete(clst)
    return jnt


# TODO: Reorder parameters
# TODO: Kwargs: input_object?, suffix, invert_scale
def create_offset(suffix='OFS', input_object=None, invert_scale=None):
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
        cmds.createNode('transform', name='null_%s' % suffix)
        return

    sel_parent = cmds.listRelatives(input_object, parent=True)

    if 'ZERO' in input_object:
        suffix = 'OFS'
    obj_short_name = lib.get_short_name(input_object)
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


# TODO: Reorder parameters
# TODO: Kwargs: input_object?, suffix, invert_scale
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


# TODO: Kwargs: translation, rotation, scale
# TODO: Make source + target required, do selections in widget command calls
    # This command will never be called through commandline via selections
def match_transformations(translation=True, rotation=True, scale=False,
                          source=None, target=None, objectSpace=False):
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
        position = cmds.xform(
            source,
            query=True,
            translation=True,
            worldSpace=not(objectSpace),
            objectSpace=objectSpace)
        cmds.xform(
            target,
            translation=position,
            worldSpace=not(objectSpace),
            objectSpace=objectSpace)
    if rotation:
        orientation = cmds.xform(
            source,
            query=True,
            rotation=True,
            worldSpace=not(objectSpace),
            objectSpace=objectSpace)
        cmds.xform(
            target,
            rotation=orientation,
            worldSpace=not(objectSpace),
            objectSpace=objectSpace)
    if scale:
        scaling = cmds.xform(source, query=True, scale=True)
        cmds.xform(target, scale=scaling)


def offset_joint_hierarchy(joints):
    """
    Offsets a hierarchy of joints with SRT groups, detaching the visible bones
    """
    # Add the new ensureArray function from the os wrapper when added to github
    # Also consider option to just select hierarchy parent to run
    for jnt in joints:
        jnt_parent = nUtil.get_parent(jnt)
        ofs = create_offset(suffix='OFS', input_object=jnt)
        create_offset(suffix='SRT', input_object=jnt)
        if jnt_parent:
            # parent to the above srt offset then clean the hierarchy children order
            cmds.parent(ofs, jnt_parent + '_SRT')
            cmds.reorder(ofs, front=True)


# TODO: Make nodes required, do selections in widget command calls
    # This command will never be called through commandline via selections
def bake_transforms_up(node=None, height=1):
    if not node:
        node = cmds.ls(selection=True)[0]

    position = cmds.getAttr(node + '.t')[0]
    rotation = cmds.getAttr(node + '.r')[0]
    transformations = position + rotation

    node_parent = node
    for i in range(height):
        node_parent = cmds.listRelatives(node_parent, parent=True)[0]

    parent_position = cmds.getAttr(node_parent + '.t')[0]
    parent_rotation = cmds.getAttr(node_parent + '.r')[0]
    parent_transformations = parent_position + parent_rotation

    new_transformations = [a + b for a, b in zip(transformations, parent_transformations)]

    scale = cmds.getAttr(node + '.s')[0]
    parent_scale = cmds.getAttr(node_parent + '.s')[0]
    new_scale = [a * b for a, b in zip(scale, parent_scale)]

    transAttrs = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')

    for attr, value in zip(transAttrs, new_transformations):
        try:
            cmds.setAttr('%s.%s' % (node_parent, attr), value)
            cmds.setAttr('%s.%s' % (node, attr), 0)
        except RuntimeError:
            # if attribute is locked, passover
            pass

    for attr in ['sx', 'sy', 'sz']:
        try:
            cmds.setAttr('%s.%s' % (node_parent, attr), new_scale[0])
            cmds.setAttr('%s.%s' % (node, attr), 1)
        except RuntimeError:
            # if attribute is locked, passover
            pass


def get_active_model_panel():
    active_model_panel = ''
    panel = cmds.getPanel(withFocus=True)
    if cmds.getPanel(typeOf=panel) == 'modelPanel':
        active_model_panel = panel
    return active_model_panel


def isolate_selection(state=True):
    selection = cmds.ls(selection=True)
    active_panel = get_active_model_panel() or DEFAULT_PANEL
    try:
        cmds.isolateSelect(active_panel, state=state)
    except RuntimeError as err:
        print err
    return selection


def get_isolate_state():
    active_panel = get_active_model_panel() or DEFAULT_PANEL
    return cmds.isolateSelect(active_panel, query=True, state=True)


def get_isolated_nodes():
    if get_isolate_state():
        active_panel = get_active_model_panel() or DEFAULT_PANEL
        isolate_selection_set = cmds.isolateSelect(active_panel, query=True, viewObjects=True)
        return cmds.sets(isolate_selection_set, query=True)
    else:
        return None


def add_isolate_nodes(nodes=[], panel=''):
    if not nodes:
        nodes = cmds.ls(selection=True)

    if not nodes:
        return False

    if not panel:
        panel = get_active_model_panel() or DEFAULT_PANEL

    cmds.select(nodes)
    try:
        cmds.isolateSelect(panel, addSelected=True)
    except RuntimeError as err:
        print err
    return nodes


def remove_isolate_nodes(nodes=[], panel=''):
    if not nodes:
        nodes = cmds.ls(selection=True)

    if not nodes:
        return False

    if not panel:
        panel = get_active_model_panel() or DEFAULT_PANEL

    cmds.select(nodes)
    cmds.isolateSelect(panel, removeSelected=True)
    return nodes


def update_isolated_nodes(nodes=[], panel=''):
    if not nodes:
        nodes = cmds.ls(selection=True)

    if not nodes:
        return False

    if not panel:
        panel = get_active_model_panel() or DEFAULT_PANEL

    cmds.isolateSelect(panel, state=False)
    cmds.select(nodes)
    cmds.isolateSelect(panel, state=True)
    # cmds.isolateSelect(panel, addSelected=True)
    return nodes


class OffsetNodeWidget(mayaFrameWidget.MayaFrameWidget):

    def __init__(self):
        mayaFrameWidget.MayaFrameWidget.__init__(self)

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
        create_joint_hierarchy = QtWidgets.QPushButton('Create Joint Offset')

        buttons_layout.addWidget(create_offset_button)
        buttons_layout.addWidget(create_child_button)
        buttons_layout.addWidget(create_joint_hierarchy)

        self.override_checkbox = QtWidgets.QCheckBox('Override Suffix')
        self.override_checkbox.setChecked(False)
        self.override_line_edit = QtWidgets.QLineEdit('')
        self.override_line_edit.setPlaceholderText('OFS')
        self.override_line_edit.setStyleSheet(
            'background-color : rgb(57, 58, 60);')
        self.override_line_edit.setEnabled(False)

        override_layout.addWidget(self.override_checkbox)
        override_layout.addWidget(self.override_line_edit)

        create_offset_button.clicked.connect(self.run_create_offset)
        create_child_button.clicked.connect(self.run_create_child)
        create_joint_hierarchy.clicked.connect(self.run_offset_joint_hierarchy)

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
            for node in cmds.ls(selection=True):
                create_offset(suffix=suffix, input_object=node)
        else:
            for node in cmds.ls(selection=True):
                create_offset(input_object=node)

    def run_create_child(self):
        if self.override_checkbox.checkState():
            suffix = self._get_suffix_parameter()
            for node in cmds.ls(selection=True):
                create_child(suffix=suffix, input_object=node)
        else:
            for node in cmds.ls(selection=True):
                create_child(input_object=node)

    def run_offset_joint_hierarchy(self):
        joints = cmds.ls(selection=True)
        offset_joint_hierarchy(joints)


class TransformWidget(mayaFrameWidget.MayaFrameWidget):

    def __init__(self):
        mayaFrameWidget.MayaFrameWidget.__init__(self)

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
        # Back transforms up
        bake_button_layout = QtWidgets.QHBoxLayout()

        transform_widget.layout().addLayout(instruction_layout)
        transform_widget.layout().addLayout(button_layout_1)
        transform_widget.layout().addLayout(button_layout_2)
        transform_widget.layout().addLayout(bake_button_layout)

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

        bake_button = QtWidgets.QPushButton('Bake Transforms Up')
        bake_button_layout.addWidget(bake_button)

        transform_button.clicked.connect(
            partial(match_transformations, True, True, False))
        translation_button.clicked.connect(
            partial(match_transformations, True, False, False))
        rotation_button.clicked.connect(
            partial(match_transformations, False, True, False))
        scale_button.clicked.connect(
            partial(match_transformations, False, False, True))

        bake_button.clicked.connect(bake_transforms_up)


class IsolateSelectionWidget(mayaFrameWidget.MayaFrameWidget):

    panel_items = {}
    snapshotted_sets = {}

    def __init__(self):
        mayaFrameWidget.MayaFrameWidget.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        isolate_widget = QtWidgets.QWidget()
        isolate_widget.setLayout(QtWidgets.QVBoxLayout())
        isolate_widget.layout().setContentsMargins(2, 2, 2, 2)
        isolate_widget.layout().setSpacing(5)
        isolate_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(isolate_widget)

        buttons_layout_1 = QtWidgets.QHBoxLayout()
        buttons_layout_2 = QtWidgets.QHBoxLayout()
        lists_layout = QtWidgets.QHBoxLayout()
        isolate_widget.layout().addLayout(buttons_layout_1)
        isolate_widget.layout().addLayout(buttons_layout_2)
        isolate_widget.layout().addLayout(lists_layout)

        isolate_button = QtWidgets.QPushButton('Isolate Selected')
        add_set_button = QtWidgets.QPushButton('Create Isolate Set')
        remove_set_button = QtWidgets.QPushButton('Remove Isolate Set')
        buttons_layout_1.addWidget(isolate_button)
        buttons_layout_1.addWidget(add_set_button)
        buttons_layout_1.addWidget(remove_set_button)

        self.set_name_line_edit = QtWidgets.QLineEdit()
        self.set_name_line_edit.setFixedWidth(125)
        self.set_name_line_edit.setPlaceholderText('ikJoints/skeleMesh/etc.')
        add_button = QtWidgets.QPushButton('Add Selected')
        remove_button = QtWidgets.QPushButton('Remove Selected')
        buttons_layout_2.addWidget(self.set_name_line_edit)
        buttons_layout_2.addWidget(add_button)
        buttons_layout_2.addWidget(remove_button)

        sets_widget = QtWidgets.QWidget()
        sets_widget.setFixedWidth(125)
        sets_widget_layout = QtWidgets.QVBoxLayout()
        sets_widget.setLayout(sets_widget_layout)
        sets_widget.layout().setContentsMargins(0, 0, 0, 0)

        self.toggle_isolate_status_button = QtWidgets.QPushButton('Toggle Isolate')
        self.isolate_sets_list = QtWidgets.QListWidget()
        self.use_selected_button = QtWidgets.QPushButton('Use this Set')

        sets_widget_layout.addWidget(self.toggle_isolate_status_button)
        sets_widget_layout.addWidget(self.isolate_sets_list)
        sets_widget_layout.addWidget(self.use_selected_button)

        self.set_nodes_list = QtWidgets.QListWidget()
        self.set_nodes_list.setFixedWidth(250)

        lists_layout.addWidget(sets_widget)
        lists_layout.addWidget(self.set_nodes_list)

        isolate_button.clicked.connect(self.create_isolate)
        add_set_button.clicked.connect(self.create_isolation_set)
        remove_set_button.clicked.connect(self.remove_isolation_set)

        add_button.clicked.connect(self.add_to_isolate)
        remove_button.clicked.connect(self.remove_from_isolate)

        self.toggle_isolate_status_button.clicked.connect(self.toggle_isolate_state)
        self.use_selected_button.clicked.connect(self.update_isolation_view)

        self.isolate_sets_list.currentItemChanged.connect(self._load_panel_objects)
        self.set_nodes_list.currentItemChanged.connect(self._select_isolated_node)

    def create_isolate(self):
        # selected = cmds.ls(selection=True)
        set_name = str(self.set_name_line_edit.text()) or 'set{}'.format(self.isolate_sets_list.count() + 1)
        if set_name in self.panel_items.keys():
            raise KeyError('Isolation set with name "{}" already exists!'.format(set_name))
        selected = isolate_selection()

        self.panel_items[set_name] = selected

        self.isolate_sets_list.addItem(set_name)
        item = self.isolate_sets_list.findItems(set_name, QtCore.Qt.MatchExactly)[0]
        self.isolate_sets_list.setCurrentItem(item)

    def _load_panel_objects(self):
        self.set_nodes_list.clear()
        try:
            current_set = self.isolate_sets_list.currentItem().text()
        except AttributeError:
            return  # state changes when list is cleared, pass over when .clear() called
        self.set_nodes_list.addItems(self.panel_items[current_set])

    def _select_isolated_node(self):
        current_item = self.set_nodes_list.currentItem()
        if current_item:
            cmds.select(current_item.text())

    def toggle_isolate_state(self):
        state = get_isolate_state()
        isolate_selection(not(state))

    def add_to_isolate(self):
        isolate_set = self.isolate_sets_list.currentItem().text()
        added_nodes = add_isolate_nodes()
        if not added_nodes:
            return
        isolated_nodes = get_isolated_nodes()

        self.set_nodes_list.clear()
        self.panel_items[isolate_set] = isolated_nodes
        self.set_nodes_list.addItems(isolated_nodes)

    def remove_from_isolate(self):
        isolate_set = self.isolate_sets_list.currentItem().text()
        removed_nodes = remove_isolate_nodes()
        if not removed_nodes:
            return
        isolated_nodes = get_isolated_nodes()

        self.set_nodes_list.clear()
        self.panel_items[isolate_set] = isolated_nodes
        self.set_nodes_list.addItems(isolated_nodes)

    def update_isolation_view(self):
        current_set = self.isolate_sets_list.currentItem().text()
        nodes_to_isolate = self.panel_items[current_set]
        update_isolated_nodes(nodes=nodes_to_isolate)

    def create_isolation_set(self):
        isolate_set_name = self.set_name_line_edit.text() or 'set{}'.format(self.isolate_sets_list.count())
        selected_nodes = cmds.ls(selection=True)

        self.isolate_sets_list.clear()
        self.panel_items[isolate_set_name] = selected_nodes
        self.isolate_sets_list.addItems(self.panel_items.keys())

        item = self.isolate_sets_list.findItems(isolate_set_name, QtCore.Qt.MatchExactly)[0]
        self.isolate_sets_list.setCurrentItem(item)

    def remove_isolation_set(self):
        isolate_set_name = self.isolate_sets_list.currentItem().text()

        self.isolate_sets_list.clear()
        del self.panel_items[isolate_set_name]
        self.isolate_sets_list.addItems(self.panel_items.keys())

        self.isolate_sets_list.setCurrentRow(0)
