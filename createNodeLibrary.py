import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui

from master_rigger import cmdsTranslator as nUtils


# Custom nodes
def float_to_three():
    ft3_node = cmds.shadingNode('unitConversion', asUtility=True)
    cmds.addAttr(ft3_node, longName='customInput', attributeType='double')
    cmds.addAttr(ft3_node, longName='customOutput', attributeType='double3')
    cmds.addAttr(ft3_node, longName='outX', attributeType='double', parent='customOutput')
    cmds.addAttr(ft3_node, longName='outY', attributeType='double', parent='customOutput')
    cmds.addAttr(ft3_node, longName='outZ', attributeType='double', parent='customOutput')

    cmds.connectAttr(ft3_node + '.customInput', ft3_node + '.outX', force=True)
    cmds.connectAttr(ft3_node + '.customInput', ft3_node + '.outY', force=True)
    cmds.connectAttr(ft3_node + '.customInput', ft3_node + '.outZ', force=True)
    return ft3_node


node_dictionary = {
    'ADL': partial(cmds.shadingNode, 'addDoubleLinear', asUtility=True),
    'BLC': partial(cmds.shadingNode, 'blendColors', asUtility=True),
    'BTA': partial(cmds.shadingNode, 'blendTwoAttr', asUtility=True),
    'CLMP': partial(cmds.shadingNode, 'clamp', asUtility=True),
    'CND': partial(cmds.shadingNode, 'condition', asUtility=True),
    'curveInfo': partial(cmds.shadingNode, 'curveInfo', asUtility=True),
    'CMPM': partial(cmds.shadingNode, 'composeMatrix', asUtility=True),
    'DCPM': partial(cmds.shadingNode, 'decomposeMatrix', asUtility=True),
    'DIST': partial(cmds.shadingNode, 'distanceBetween', asUtility=True),
    'FTT': float_to_three,
    'MDL': partial(cmds.shadingNode, 'multDoubleLinear', asUtility=True),
    'MDIV': partial(cmds.shadingNode, 'multiplyDivide', asUtility=True),
    'MM': partial(cmds.shadingNode, 'multMatrix', asUtility=True),
    'PMA': partial(cmds.shadingNode, 'plusMinusAverage', asUtility=True),
    'REV': partial(cmds.shadingNode, 'reverse', asUtility=True),
    'RMPV': partial(cmds.shadingNode, 'remapValue', asUtility=True),
    'SR': partial(cmds.shadingNode, 'setRange', asUtility=True),
    'UC': partial(cmds.shadingNode, 'unitConversion', asUtility=True),
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
    'composeMatrix': 'CMPM',
    'CMPM': 'CMPM',
    'decomposeMatrix': 'DCPM',
    'DCPM': 'DCPM',
    'distanceBetween': 'DIST',
    'DIST': 'DIST',
    'floatTo3': 'FTT',
    'floatToThree': 'FTT',
    'FTT': 'FTT',
    'multDoubleLinear': 'MDL',
    'MDL': 'MDL',
    'multiplyDivide': 'MDIV',
    'MDIV': 'MDIV',
    'multMatrix': 'MM',
    'MM': 'MM',
    'plusMinusAverage': 'PMA',
    'PMA': 'PMA',
    'reverse': 'REV',
    'REV': 'REV',
    'remapValue': 'RMPV',
    'RMPV': 'RMPV',
    'setRange': 'SR',
    'SR': 'SR',
    'unitConversion': 'UC',
    'UC': 'UC',
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


# Matrix stuff needs major field testing.  Try out at work
def simple_matrix_constraint(target=None, source=None, position=True,
                             orientation=True, scale=False,
                             maintain_offset=True):

    if not target:
        try:
            target = nUtils.get_selection_list()[0]
        except Exception as err:
            raise err

    if not source:
        try:
            source = nUtils.get_selection_list()[1]
        except Exception as err:
            raise err

    decompose_node = create_node(node_key='DCPM',
                                 name='{}_matrixSRT'.format(target))

    if maintain_offset:
        cmds.connectAttr(source + '.matrix', decompose_node)
    else:
        cmds.connectAttr(source + '.worldMatrix[0]', decompose_node)

    if position:
        cmds.connectAttr(decompose_node + '.outputTranslate', target + '.t')
    if orientation:
        cmds.connectAttr(decompose_node + '.outputRotate', target + '.r')
    if scale:
        cmds.connectAttr(decompose_node + '.outputScale', target + '.s')


def matrix_constraint(target=None, source=None, position=True, orientation=True,
                      scale=False):

    # Order of matrix operation conditions:
    # - check values of the source object
    # - understand the position hierarchy of the source
    # - find the parent matrix of the source within its correct hierarchy
    #   * if the local matrix == worldMatrix, use world inverse and skip hierarchy sorting
    # - create a multMatrix based on the inverse parent and local matrix of the source
    # - decompose the multMatrix to send values to the target

    if not target:
        try:
            target = nUtils.get_selection_list()[0]
        except Exception as err:
            raise err

    if not source:
        try:
            source = nUtils.get_selection_list()[1]
        except Exception as err:
            raise err

    local_matrix = nUtils.get_matrix(source)
    world_matrix = nUtils.get_world_matrix(source)

    # if the local == world, hierarchy is irrelevant
    if local_matrix == world_matrix:
        simple_matrix_constraint(target=target, source=source, position=position,
                                 orientation=orientation, scale=scale)
        return

    null_matrix = [1, 0, 0, 0,
                   0, 1, 0, 0,
                   0, 0, 1, 0,
                   0, 0, 0, 1]

    source_parent = nUtils.get_parent(source)
    parent_matrix = nUtils.get_matrix(source_parent)

    # check if this properly rounds to 0 for insignificant values
    # Loops through parents until one with an offset value is found
    while null_matrix == parent_matrix:
        new_parent = nUtils.get_parent(source_parent)
        parent_matrix = nUtils.get_matrix(new_parent)
        source_parent = new_parent
        # on final loop, source_parent will be the correct transform

    parent_world_inverse_matrix = '{}.worldInverseMatrix'.format(source_parent)
    world_matrix = '{}.worldMatrix'.format(source)

    mult_matrix_node = create_node(node_key='MM',
                                   name='{}_matrixSRT'.format(target))

    decompose_node = create_node(node_key='DCPM',
                                 name='{}_matrixSRT'.format(target))

    cmds.connectAttr(world_matrix, mult_matrix_node + '.inputMatrix[0]')
    cmds.connectAttr(parent_world_inverse_matrix,
                     mult_matrix_node + '.inputMatrix[1]')
    cmds.connectAttr(mult_matrix_node + '.outputMatrix',
                     decompose_node + '.inputMatrix')

    if position:
        cmds.connectAttr(decompose_node + '.outputTranslate', target + '.t')
    if orientation:
        cmds.connectAttr(decompose_node + '.outputRotate', target + '.r')
    if scale:
        cmds.connectAttr(decompose_node + '.outputScale', target + '.s')


def duplicate_node_connections(find, replace, nodes=[]):
    if not nodes:
        nodes = cmds.ls(selection=True)
    cmds.select(clear=True)
    newNodes = []

    for node in nodes:
        # Run by itself to create all nodes immediately
        newNode = cmds.duplicate(node, name=node.replace(find, replace))
        newNodes.append(newNode)

    for node in nodes:
        nodeConnections = [
            con for con in cmds.listConnections(
                node, connections=True, source=True, destination=False)
            if '.' in con and not con.endswith('.message')
        ]

        for connection in nodeConnections:
            sourceAttr = cmds.connectionInfo(connection, sourceFromDestination=True)
            sourceAttr = sourceAttr.replace(find, replace)
            targetAttr = connection.replace(find, replace)
            cmds.connectAttr(sourceAttr, targetAttr, force=True)


class NodeWidget(QtWidgets.QFrame):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        node_widget = QtWidgets.QWidget()
        node_widget.setLayout(QtWidgets.QVBoxLayout())
        node_widget.layout().setContentsMargins(2, 2, 2, 2)
        node_widget.layout().setSpacing(5)
        node_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(node_widget)

        name_layout = QtWidgets.QHBoxLayout()
        type_layout = QtWidgets.QHBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        # Add a small splitter
        find_layout = QtWidgets.QHBoxLayout()
        replace_layout = QtWidgets.QHBoxLayout()
        dup_button_layout = QtWidgets.QHBoxLayout()

        node_widget.layout().addLayout(name_layout)
        node_widget.layout().addLayout(type_layout)
        node_widget.layout().addLayout(button_layout)
        # add small splitter
        node_widget.layout().addLayout(find_layout)
        node_widget.layout().addLayout(replace_layout)
        node_widget.layout().addLayout(dup_button_layout)

        node_label = QtWidgets.QLabel('Node Name:')
        self.input_node_name = QtWidgets.QLineEdit()
        self.input_node_name.setPlaceholderText('prefix_nodeName')  # Grey text

        reg_ex = QtCore.QRegExp('^(?!@$^_)[a-zA-Z_#_0-9]+')
        text_validator = QtGui.QRegExpValidator(reg_ex, self.input_node_name)
        self.input_node_name.setValidator(text_validator)

        name_layout.addWidget(node_label)
        name_layout.addWidget(self.input_node_name)

        node_type_label = QtWidgets.QLabel('Node Type:')
        self.node_type_combo = QtWidgets.QComboBox()
        # Adding combo box items for node options
        for node in sorted(node_name_dictionary.keys()):
            if node[0] == node[0].lower():
                self.node_type_combo.addItem(node)
        type_layout.addWidget(node_type_label)
        type_layout.addWidget(self.node_type_combo)

        # Show Node name example
        self.node_display_example = QtWidgets.QLabel('')

        create_node_button = QtWidgets.QPushButton('Create Node')

        button_layout.addWidget(self.node_display_example)
        button_layout.addWidget(create_node_button)

        # Duplicate Node Network widgets
        find_label = QtWidgets.QLabel('Find:')
        self.find_name = QtWidgets.QLineEdit()
        self.find_name.setPlaceholderText('L_')  # Grey text

        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_name)

        # Duplicate Node Network widgets -----------
        replace_label = QtWidgets.QLabel('Replace:')
        self.replace_name = QtWidgets.QLineEdit()
        self.replace_name.setPlaceholderText('R_')  # Grey text

        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_name)

        duplicate_network_button = QtWidgets.QPushButton('Duplicate Node Network')
        dup_button_layout.addWidget(duplicate_network_button)

        # ------------------------------------------

        self.node_type_combo.currentIndexChanged.connect(self._update_node_name)
        self.input_node_name.textChanged.connect(self._update_node_name)

        create_node_button.clicked.connect(self._get_node_settings)
        duplicate_network_button.clicked.connect(self._duplicate_node_network)

        self._update_node_name()

    def _get_node_settings(self):
        node_key = node_name_dictionary[self.node_type_combo.currentText()]
        node_name = str(self.input_node_name.text()).strip()
        if not node_name:
            node_name = self.node_type_combo.currentText()

        create_node(node_key=node_key, name=node_name)

    def _update_node_name(self):
        input_text = str(self.input_node_name.text()).strip()

        node_key = self.node_type_combo.currentText()
        node_text = node_name_dictionary[node_key]

        if not input_text:
            self.node_display_example.setText('<font color=#646464>e.g.</font>')
            return

        self.node_display_example.setText(
            '<font color=#646464>e.g. %s_%s</font>' % (input_text, node_text))

    def _duplicate_node_network(self):
        find_text = str(self.find_name.text()).strip()
        replace_text = str(self.replace_name.text()).strip()

        duplicate_node_connections(find=find_text, replace=replace_text)
