import maya.cmds as cmds
# import maya.mel as mel
import pymel.core as pm
# from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from maya_tools import mayaFrameWidget
# import re

import Splitter
from master_rigger.data import node_data
# from master_rigger import cmdsTranslator as nUtils
reload(node_data)

plugin_node_name_dictionary = {}


# Use math nodes if loaded
if cmds.pluginInfo('mayaMathNodes', query=True, loaded=True):
    plugin_node_name_dictionary.update(node_data.MATH_NODE_DICTIONARY)

if cmds.pluginInfo('arkMayaNodes', query=True, loaded=True):
    plugin_node_name_dictionary.update(node_data.ARK_NODE_DICTIONARY)


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
    selection = pm.ls(selection=True)

    try:
        node = node_data.NODE_DICTIONARY[node_data.NODE_NAME_DICTIONARY[node_key]]()
    except:  # check exception type
        raise Exception('Node type ({}) not yet implemented!'.format(node_key))

    if not name:
        if selection:
            name = selection[0].name()
        else:
            name = node.type()

    node.rename('%s_%s' % (name, node_data.NODE_NAME_DICTIONARY[node_key]))
    return node.name()


# Long-term future goal:
# convert to create_custom_node when more than one plug-in added to personal library
def create_plugin_node(plugin_node_key, name=None):
    plug_prefix = NodeWidget.get_plugin_node_prefix(plugin_node_key)
    plug_namespace = NodeWidget.get_plugin_node_namespace(plugin_node_key)

    try:
        node = cmds.createNode(plug_prefix + plugin_node_key)
    except:  # check exception type
        raise TypeError('Incorrect nodeType: pluginNode({}) !'.format(plugin_node_key))

    if not cmds.namespace(exists=plug_namespace):
        cmds.namespace(add=plug_namespace)

    if not name:
        if cmds.ls(selection=True):
            name = cmds.ls(selection=True)[0]
        else:
            name = cmds.objectType(node).strip(plug_prefix)

    plugin_node_suffix = plugin_node_name_dictionary[plugin_node_key] or plugin_node_key.upper()

    node_name = cmds.rename(node,
                            '{plugin}:{name}_{suffix}'.format(
                                plugin=plug_namespace,
                                name=name,
                                suffix=plugin_node_suffix))
    return node_name


def duplicate_node_connections(find, replace, nodes=[]):
    if not nodes:
        nodes = cmds.ls(selection=True)
    cmds.select(clear=True)
    newNodes = []

    for node in nodes:
        new_node_name = node.replace(find, replace)
        newNode = cmds.duplicate(node, name=new_node_name)
        newNodes.append(newNode)

    for node in nodes:
        # Input Connections
        nodeInConnections = [
            con for con in cmds.listConnections(
                node, connections=True, source=True, destination=False, skipConversionNodes=True)
            if '.' in con and not con.endswith('.message')
        ]

        for connection in nodeInConnections:
            sourceAttr = cmds.connectionInfo(connection, sourceFromDestination=True)
            if cmds.objectType(sourceAttr.split('.')[0]) == 'unitConversion':
                unitConversionInOut = sourceAttr.replace('output', 'input')
                sourceAttr = cmds.connectionInfo(
                    unitConversionInOut,
                    sourceFromDestination=True)
            sourceAttr = sourceAttr.replace(find, replace)
            targetAttr = connection.replace(find, replace)
            cmds.connectAttr(sourceAttr, targetAttr, force=True)

        # Output Connections
        nodeOutConnections = [
            con for con in cmds.listConnections(
                node, connections=True, source=False, destination=True, skipConversionNodes=True)
            if '.' in con and not con.endswith('.message')
        ]
        for connection in nodeOutConnections:
            targetAttrs = cmds.connectionInfo(connection, destinationFromSource=True)
            sourceAttr = connection.replace(find, replace)
            for targetAttr in targetAttrs:
                if cmds.objectType(targetAttr.split('.')[0]) == 'unitConversion':
                    unitConversionInOut = targetAttr.replace('input', 'output')
                    targetAttr = cmds.connectionInfo(
                        unitConversionInOut,
                        destinationFromSource=True)
                    for con in targetAttr:
                        con = con.replace(find, replace)
                        cmds.connectAttr(sourceAttr, con, force=True)
                else:
                    targetAttr = targetAttr.replace(find, replace)
                    cmds.connectAttr(sourceAttr, targetAttr, force=True)


class NodeWidget(mayaFrameWidget.MayaFrameWidget):

    def __init__(self):
        mayaFrameWidget.MayaFrameWidget.__init__(self)

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

        # Regular node layouts
        name_layout = QtWidgets.QHBoxLayout()
        type_layout = QtWidgets.QHBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        # Duplicate node layouts
        find_layout = QtWidgets.QHBoxLayout()
        replace_layout = QtWidgets.QHBoxLayout()
        dup_button_layout = QtWidgets.QHBoxLayout()
        # Plugin node layouts
        plugin_name_layout = QtWidgets.QHBoxLayout()
        plugin_type_layout = QtWidgets.QHBoxLayout()
        plugin_button_layout = QtWidgets.QHBoxLayout()

        node_widget.layout().addLayout(name_layout)
        node_widget.layout().addLayout(type_layout)
        node_widget.layout().addLayout(button_layout)

        node_widget.layout().addLayout(Splitter.SplitterLayout())

        node_widget.layout().addLayout(find_layout)
        node_widget.layout().addLayout(replace_layout)
        node_widget.layout().addLayout(dup_button_layout)

        node_widget.layout().addLayout(Splitter.SplitterLayout())

        node_widget.layout().addLayout(plugin_name_layout)
        node_widget.layout().addLayout(plugin_type_layout)
        node_widget.layout().addLayout(plugin_button_layout)

        # Create Nodes widgets --------------------------------------------- #
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
        for node in sorted(node_data.NODE_NAME_DICTIONARY.keys()):
            if node[0] == node[0].lower():
                self.node_type_combo.addItem(node)
        type_layout.addWidget(node_type_label)
        type_layout.addWidget(self.node_type_combo)

        # Show Node name example
        self.node_display_example = QtWidgets.QLabel('')

        create_node_button = QtWidgets.QPushButton('Create Node')

        button_layout.addWidget(self.node_display_example)
        button_layout.addWidget(create_node_button)

        # Duplicate Node Network widgets ------------------------------------ #
        find_label = QtWidgets.QLabel('Find:')
        self.find_name = QtWidgets.QLineEdit()
        self.find_name.setPlaceholderText('L_')  # Grey text

        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_name)

        # Create Plugin Node widgets ---------------------------------------- #
        plugin_node_label = QtWidgets.QLabel('Custom Node Name:')
        self.input_plugin_node_name = QtWidgets.QLineEdit()
        self.input_plugin_node_name.setPlaceholderText('prefix_nodeName')  # Grey text

        plugin_text_validator = QtGui.QRegExpValidator(reg_ex, self.input_plugin_node_name)
        self.input_plugin_node_name.setValidator(plugin_text_validator)

        plugin_name_layout.addWidget(plugin_node_label)
        plugin_name_layout.addWidget(self.input_plugin_node_name)

        plugin_node_type_label = QtWidgets.QLabel('Plugin Node Type:')
        self.plugin_node_type_combo = QtWidgets.QComboBox()
        # Adding combo box items for node options
        for node in sorted(plugin_node_name_dictionary.keys()):
            self.plugin_node_type_combo.addItem(node)
        plugin_type_layout.addWidget(plugin_node_type_label)
        plugin_type_layout.addWidget(self.plugin_node_type_combo)

        # Show Node name example
        self.plugin_node_display_example = QtWidgets.QLabel('')

        create_plugin_node_button = QtWidgets.QPushButton('Create Node')

        plugin_button_layout.addWidget(self.plugin_node_display_example)
        plugin_button_layout.addWidget(create_plugin_node_button)

        # Duplicate Node Network widgets ------------------------------------ #
        replace_label = QtWidgets.QLabel('Replace:')
        self.replace_name = QtWidgets.QLineEdit()
        self.replace_name.setPlaceholderText('R_')  # Grey text

        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_name)

        duplicate_network_button = QtWidgets.QPushButton('Duplicate Node Network')
        dup_button_layout.addWidget(duplicate_network_button)

        # ------------------------------------------------------------------- #

        self.node_type_combo.currentIndexChanged.connect(self._update_node_name)
        self.plugin_node_type_combo.currentIndexChanged.connect(self._update_plugin_node_name)
        self.input_node_name.textChanged.connect(self._update_node_name)
        self.input_plugin_node_name.textChanged.connect(self._update_plugin_node_name)

        create_node_button.clicked.connect(self._get_node_settings)
        duplicate_network_button.clicked.connect(self._duplicate_node_network)
        create_plugin_node_button.clicked.connect(self._get_plugin_node_settings)

        self._update_node_name()

    @classmethod
    def get_plugin_node_prefix(cls, plugin_node_key):
        plug_prefix = None
        for data in node_data.PLUGIN_LIBRARIES.values():
            if plugin_node_key in data['library'].keys():
                plug_prefix = data['prefix']
                break
        return plug_prefix

    @classmethod
    def get_plugin_node_namespace(cls, plugin_node_key):
        plug_namespace = None
        for data in node_data.PLUGIN_LIBRARIES.values():
            if plugin_node_key in data['library'].keys():
                plug_namespace = data['namespace']
                break
        return plug_namespace

    def _get_node_settings(self):
        node_key = node_data.NODE_NAME_DICTIONARY[self.node_type_combo.currentText()]
        node_name = str(self.input_node_name.text()).strip()
        if not node_name:
            node_name = self.node_type_combo.currentText()

        create_node(node_key=node_key, name=node_name)

    def _get_plugin_node_settings(self):
        node_key = self.plugin_node_type_combo.currentText()
        node_name = str(self.input_plugin_node_name.text()).strip()
        if not node_name:
            node_name = self.plugin_node_type_combo.currentText()

        create_plugin_node(plugin_node_key=node_key, name=node_name)

    def _update_node_name(self):
        input_text = str(self.input_node_name.text()).strip()

        node_key = self.node_type_combo.currentText()
        node_text = node_data.NODE_NAME_DICTIONARY[node_key]

        if not input_text:
            self.node_display_example.setText('<font color=#646464>e.g.</font>')
            return

        self.node_display_example.setText(
            '<font color=#646464>e.g. %s_%s</font>' % (input_text, node_text))

    def _update_plugin_node_name(self):
        input_text = str(self.input_plugin_node_name.text()).strip()

        plugin_node_key = self.plugin_node_type_combo.currentText()
        plugin_node_text = plugin_node_name_dictionary[plugin_node_key]

        plugin_namespace = NodeWidget.get_plugin_node_namespace(plugin_node_key)

        if not input_text:
            self.plugin_node_display_example.setText('<font color=#646464>e.g.</font>')
            return

        self.plugin_node_display_example.setText(
            '<font color=#646464>e.g. {plugin}:{name}_{nodeType}</font>'.format(
                plugin=plugin_namespace,  # change to plugin at later date
                name=input_text,
                nodeType=plugin_node_text
            )
        )

    def _duplicate_node_network(self):
        find_text = str(self.find_name.text()).strip()
        replace_text = str(self.replace_name.text()).strip()

        duplicate_node_connections(find=find_text, replace=replace_text)
