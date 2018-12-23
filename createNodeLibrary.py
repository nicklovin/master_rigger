import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui

node_dictionary = {
    'ADL': partial(cmds.shadingNode, 'addDoubleLinear', asUtility=True),
    'BLC': partial(cmds.shadingNode, 'blendColors', asUtility=True),
    'BTA': partial(cmds.shadingNode, 'blendTwoAttr', asUtility=True),
    'CLMP': partial(cmds.shadingNode, 'clamp', asUtility=True),
    'CND': partial(cmds.shadingNode, 'condition', asUtility=True),
    'curveInfo': partial(cmds.shadingNode, 'curveInfo', asUtility=True),
    'DCPM': partial(cmds.shadingNode, 'decomposeMatrix', asUtility=True),
    'DIST': partial(cmds.shadingNode, 'distanceBetween', asUtility=True),
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
    'decomposeMatrix': 'DCPM',
    'DCPM': 'DCPM',
    'distanceBetween': 'DIST',
    'DIST': 'DIST',
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


def matrix_constraint():
    pass


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

        node_widget.layout().addLayout(name_layout)
        node_widget.layout().addLayout(type_layout)
        node_widget.layout().addLayout(button_layout)

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

        self.node_type_combo.currentIndexChanged.connect(self._update_node_name)
        self.input_node_name.textChanged.connect(self._update_node_name)

        create_node_button.clicked.connect(self._get_node_settings)

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
