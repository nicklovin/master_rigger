import maya.cmds as cmds
import maya.mel as mel
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
# import re

import Splitter

# from master_rigger import cmdsTranslator as nUtils

plugin_node_name_dictionary = {}


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
    'blendROT': partial(cmds.shadingNode, 'animBlendNodeAdditiveRotation', asUtility=True),
    'BLC': partial(cmds.shadingNode, 'blendColors', asUtility=True),
    'BTA': partial(cmds.shadingNode, 'blendTwoAttr', asUtility=True),
    'CFME': partial(cmds.shadingNode, 'curveFromMeshEdge', asUtility=True),
    'CLMP': partial(cmds.shadingNode, 'clamp', asUtility=True),
    'CMPM': partial(cmds.shadingNode, 'composeMatrix', asUtility=True),
    'CND': partial(cmds.shadingNode, 'condition', asUtility=True),
    'CPOS': partial(cmds.shadingNode, 'closestPointOnSurface', asUtility=True),
    'curveInfo': partial(cmds.shadingNode, 'curveInfo', asUtility=True),
    'DCPM': partial(cmds.shadingNode, 'decomposeMatrix', asUtility=True),
    'DIST': partial(cmds.shadingNode, 'distanceBetween', asUtility=True),
    '4x4M': partial(cmds.shadingNode, 'fourByFourMatrix', asUtility=True),
    'FTT': float_to_three,
    'INVM': partial(cmds.shadingNode, 'inverseMatrix', asUtility=True),
    'LOFT': partial(cmds.shadingNode, 'loft', asUtility=True),
    'MDIV': partial(cmds.shadingNode, 'multiplyDivide', asUtility=True),
    'MDL': partial(cmds.shadingNode, 'multDoubleLinear', asUtility=True),
    'MM': partial(cmds.shadingNode, 'multMatrix', asUtility=True),
    'PMA': partial(cmds.shadingNode, 'plusMinusAverage', asUtility=True),
    'PMM': partial(cmds.shadingNode, 'pointMatrixMult', asUtility=True),
    'POCI': partial(cmds.shadingNode, 'pointOnCurveInfo', asUtility=True),
    'POSI': partial(cmds.shadingNode, 'pointOnSurfaceInfo', asUtility=True),
    'REV': partial(cmds.shadingNode, 'reverse', asUtility=True),
    'RMPV': partial(cmds.shadingNode, 'remapValue', asUtility=True),
    'SR': partial(cmds.shadingNode, 'setRange', asUtility=True),
    'UC': partial(cmds.shadingNode, 'unitConversion', asUtility=True),
    'VP': partial(cmds.shadingNode, 'vectorProduct', asUtility=True),
}

math_node_dictionary = {
    'Absolute': 'ABS',
    'AbsoluteAngle': 'angABS',
    'AbsoluteInt': 'intABS',
    'Acos': 'ACOS',
    'Add': 'ADD',
    'AddAngle': 'angADD',
    'AddInt': 'intADD',
    'AddVector': 'vecADD',
    'AndBool': 'AND',
    'AndInt': None,
    'AngleBetweenVectors': 'angBTWN',
    'Asin': 'ASIN',
    'Atan': 'ATAN',
    'Atan2': 'ATAN2INPUT',
    'Average': 'AVG',
    'AverageAngle': 'angAVG',
    'AverageInt': 'intAVG',
    'AverageMatrix': 'mtxAVG',
    'AverageQuaternion': 'quatAVG',
    'AverageRotation': 'rotAVG',
    'AverageVector': 'vecAVG',
    'AxisFromMatrix': None,
    'Ceil': 'CEIL',
    'CeilAngle': 'angCEIL',
    'Clamp': 'CLMP',
    'ClampAngle': 'angCLMP',
    'ClampInt': 'intCLMP',
    'Compare': None,
    'CompareAngle': None,
    'CompareInt': None,
    'CosAngle': 'COS',
    'CrossProduct': 'CROSS',
    'DebugLog': None,
    'DebugLogAngle': None,
    'DebugLogInt': None,
    'DebugLogMatrix': None,
    'DebugLogQuaternion': None,
    'DebugLogRotation': None,
    'DebugLogVector': None,
    'DistancePoints': None,
    'DistanceTransforms': None,
    'Divide': 'DIV',
    'DivideAngle': 'angDIV',
    'DivideAngleByInt': 'angXintDIV',
    'DivideByInt': 'intDIV',
    'DotProduct': 'DOT',
    'Floor': 'FLOOR',
    'FloorAngle': 'angFLOOR',
    'InverseMatrix': 'mtxINV',
    'InverseQuaternion': 'quatINV',
    'InverseRotation': 'rotINV',
    'Lerp': None,
    'LerpAngle': None,
    'LerpMatrix': None,
    'LerpVector': None,
    'MatrixFromDirection': 'DIR2MTX',
    'MatrixFromQuaternion': 'QUAT2MTX',
    'MatrixFromRotation': 'ROT2MTX',
    'MatrixFromTRS': 'SRT2MTX',
    'Max': 'MAX',
    'MaxAngle': 'angMAX',
    'MaxAngleElement': 'angMAXinARRAY',
    'MaxElement': 'MAXinARRAY',
    'MaxInt': 'intMAX',
    'MaxIntElement': 'intMAXinARRAY',
    'Max': 'MIN',
    'MinAngle': 'angMIN',
    'MinAngleElement': 'angMINinARRAY',
    'MinElement': 'MINinARRAY',
    'MinInt': 'intMIN',
    'MinIntElement': 'intMINinARRAY',
    'ModulusInt': 'REMAINDER',
    'Multiply': 'MULT',
    'MultiplyAngle': 'angMULT',
    'MultiplyAngleByInt': 'angXintMULT',
    'MultiplyByInt': 'fltXintMULT',
    'MultiplyInt': 'intMULT',
    'MultiplyMatrix': 'mtxMULT',
    'MultiplyQuaternion': 'quatMULT',
    'MultiplyRotation': 'rotMULT',
    'MultiplyVector': 'vecMULT',
    'MultiplyVectorByMatrix': 'vecXmtxMULT',
    'Negate': 'NEG',
    'NegateAngle': 'angNEG',
    'NegateInt': 'intNEG',
    'NegateVector': 'vecNEG',
    'NormalizeArray': None,
    'NormalizeVector': None,
    'NormalizeWeightsArray': None,
    'NotBool': 'NOT',
    'OrBool': 'OR',
    'OrInt': None,
    'Power': 'POW',
    'QuaternionFromMatrix': 'MTX2QUAT',
    'QuaternionFromRotation': 'ROT2QUAT',
    'Remap': 'RMP',
    'RemapAngle': 'angRMP',
    'RemapInt': 'intRMP',
    'RotationFromMatrix': 'MTX2ROT',
    'RotationFromQuaternion': 'QUAT2ROT',
    'Round': 'ROUND',
    'RoundAngle': 'angROUND',
    'ScaleFromMatrix': 'MTX2SCALE',
    'Select': 'SWITCH',
    'SelectAngle': 'angSWITCH',
    'SelectAngleArray': 'angArraySWITCH',
    'SelectArray': 'arraySWITCH',
    'SelectCurve': 'crvSWITCH',
    'SelectInt': 'intSWITCH',
    'SelectIntArray': 'intArraySWITCH',
    'SelectMatrix': 'mtxSWITCH',
    'SelectMatrixArray': 'mtxArraySWITCH',
    'SelectMesh': 'meshSWITCH',
    'SelectQuaternion': 'quatSWITCH',
    'SelectRotation': 'rotSWITCH',
    'SelectSurface': 'surfSWITCH',
    'SelectVector': 'vecSWITCH',
    'SelectVectorArray': 'vecArraySWITCH',
    'SinAngle': 'SIN',
    'SlerpQuaternion': None,
    'Smoothstep': None,
    'SquareRoot': 'SQRT',
    'Subtract': 'SUBTRACT',
    'SubtractAngle': 'angSUBTRACT',
    'SubtractInt': 'intSUBTRACT',
    'SubtractVector': 'vecSUBTRACT',
    'Sum': 'SUM',
    'SumAngle': 'angSUM',
    'SumInt': 'intSUM',
    'SumVector': 'vecSUM',
    'TanAngle': 'TAN',
    'TranslationFromMatrix': 'MTX2POS',
    'TwistFromMatrix': 'MTX2TWIST',
    'TwistFromRotation': 'ROT2TWIST',
    'VectorLength': 'VECLEN',
    'VectorLengthSquared': 'VECLENSQ',
    'WeightedAverage': None,
    'WeightedAverageAngle': None,
    'WeightedAverageInt': None,
    'WeightedAverageMatrix': None,
    'WeightedAverageQuaternion': None,
    'WeightedAverageRotation': None,
    'WeightedAverageVector': None,
    'XorBool': None,
    'XorInt': None,
}

node_name_dictionary = {
    'addDoubleLinear': 'ADL',
    'ADL': 'ADL',
    'animBlendNodeAdditiveRotation': 'blendROT',
    'blendROT': 'blendROT',
    'blendColors': 'BLC',
    'BLC': 'BLC',
    'blendTwoAttr': 'BTA',
    'BTA': 'BTA',
    'clamp': 'CLMP',
    'CLMP': 'CLMP',
    'closestPointOnSurface': 'CPOS',
    'CPOS': 'CPOS',
    'condition': 'CND',
    'CND': 'CND',
    'curveFromMeshEdge': 'CFME',
    'CFME': 'CFME',
    'curveInfo': 'curveInfo',
    'composeMatrix': 'CMPM',
    'CMPM': 'CMPM',
    'decomposeMatrix': 'DCPM',
    'DCPM': 'DCPM',
    'distanceBetween': 'DIST',
    'DIST': 'DIST',
    'fourByFourMatrix': '4x4M',
    'FBFM': '4x4M',
    '4x4M': '4x4M',
    'floatTo3': 'FTT',
    'FTT': 'FTT',
    'inverseMatrix': 'INVM',
    'INVM': 'INVM',
    'loft': 'LOFT',
    'LOFT': 'LOFT',
    'multDoubleLinear': 'MDL',
    'MDL': 'MDL',
    'multiplyDivide': 'MDIV',
    'MDIV': 'MDIV',
    'multMatrix': 'MM',
    'MM': 'MM',
    'plusMinusAverage': 'PMA',
    'PMA': 'PMA',
    'pointMatrixMult': 'PMM',
    'PMM': 'PMM',
    'pointOnCurveInfo': 'POCI',
    'POCI': 'POCI',
    'pointOnSurfaceInfo': 'POSI',
    'POSI': 'POSI',
    'reverse': 'REV',
    'REV': 'REV',
    'remapValue': 'RMPV',
    'RMPV': 'RMPV',
    'setRange': 'SR',
    'SR': 'SR',
    'unitConversion': 'UC',
    'UC': 'UC',
    'vectorProduct': 'VP',
    'VECP': 'VP',
    'VP': 'VP',
}


# Use math nodes if loaded
if cmds.pluginInfo('mayaMathNodes', query=True, loaded=True):
    math_node_prefix = 'math_'
    math_node_namespace = 'MMM'
    plugin_node_name_dictionary.update(math_node_dictionary)


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
    try:
        node = node_dictionary[node_name_dictionary[node_key]]()
    except:  # check exception type
        raise Exception('Node type ({}) not yet implemented!'.format(node_key))

    if not name:
        if cmds.ls(selection=True):
            name = cmds.ls(selection=True)[0]
        else:
            name = cmds.objectType(node)

    node_name = cmds.rename(node,
                            '%s_%s' % (name, node_name_dictionary[node_key]))
    return node_name


# Long-term future goal:
# convert to create_custom_node when more than one plug-in added to personal library
def create_plugin_node(plugin_node_key, name=None):
    try:
        node = cmds.createNode(math_node_prefix + plugin_node_key)
    except:  # check exception type
        raise TypeError('Incorrect nodeType: mayaMathNode({}) !'.format(plugin_node_key))

    if not cmds.namespace(exists=math_node_namespace):
        cmds.namespace(add=math_node_namespace)

    if not name:
        if cmds.ls(selection=True):
            name = cmds.ls(selection=True)[0]
        else:
            name = cmds.objectType(node).strip(math_node_prefix)

    math_node_suffix = plugin_node_name_dictionary[plugin_node_key] or plugin_node_key.upper()

    node_name = cmds.rename(node,
                            '{plugin}:{name}_{suffix}'.format(
                                plugin=math_node_namespace,
                                name=name,
                                suffix=math_node_suffix))
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
                sourceAttr = cmds.connectionInfo(unitConversionInOut, sourceFromDestination=True)
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
                    targetAttr = cmds.connectionInfo(unitConversionInOut, destinationFromSource=True)
                    for con in targetAttr:
                        con = con.replace(find, replace)
                        cmds.connectAttr(sourceAttr, con, force=True)
                else:
                    targetAttr = targetAttr.replace(find, replace)
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

        # Duplicate Node Network widgets ------------------------------------ #
        find_label = QtWidgets.QLabel('Find:')
        self.find_name = QtWidgets.QLineEdit()
        self.find_name.setPlaceholderText('L_')  # Grey text

        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_name)

        # Duplicate Node Network widgets ------------------------------------ #
        replace_label = QtWidgets.QLabel('Replace:')
        self.replace_name = QtWidgets.QLineEdit()
        self.replace_name.setPlaceholderText('R_')  # Grey text

        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_name)

        duplicate_network_button = QtWidgets.QPushButton('Duplicate Node Network')
        dup_button_layout.addWidget(duplicate_network_button)

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

        # ------------------------------------------------------------------- #

        self.node_type_combo.currentIndexChanged.connect(self._update_node_name)
        self.input_node_name.textChanged.connect(self._update_node_name)
        self.input_plugin_node_name.textChanged.connect(self._update_plugin_node_name)

        create_node_button.clicked.connect(self._get_node_settings)
        duplicate_network_button.clicked.connect(self._duplicate_node_network)
        create_plugin_node_button.clicked.connect(self._get_plugin_node_settings)

        self._update_node_name()

    def _get_node_settings(self):
        node_key = node_name_dictionary[self.node_type_combo.currentText()]
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
        node_text = node_name_dictionary[node_key]

        if not input_text:
            self.node_display_example.setText('<font color=#646464>e.g.</font>')
            return

        self.node_display_example.setText(
            '<font color=#646464>e.g. %s_%s</font>' % (input_text, node_text))

    def _update_plugin_node_name(self):
        input_text = str(self.input_plugin_node_name.text()).strip()

        plugin_node_key = self.plugin_node_type_combo.currentText()
        plugin_node_text = plugin_node_name_dictionary[plugin_node_key]

        if not input_text:
            self.plugin_node_display_example.setText('<font color=#646464>e.g.</font>')
            return

        self.plugin_node_display_example.setText(
            '<font color=#646464>e.g. {plugin}:{name}_{nodeType}</font>'.format(
                plugin=math_node_namespace,  # change to plugin at later date
                name=input_text,
                nodeType=plugin_node_text
            )
        )

    def _duplicate_node_network(self):
        find_text = str(self.find_name.text()).strip()
        replace_text = str(self.replace_name.text()).strip()

        duplicate_node_connections(find=find_text, replace=replace_text)
