import maya.cmds as cmds
# from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from maya_tools.widgets import mayaFrameWidget
from master_rigger import createNodeLibrary as node
from master_rigger import curve_assignment as crv
from master_rigger import basicTools as tool
from master_rigger import cmdsTranslator as nUtils
# import renamerLibrary as lib
reload(node)
reload(crv)
reload(tool)
reload(nUtils)
reload(mayaFrameWidget)


def vector_aim_constraint(source, target, up_position, aim_vector='x', up_vector='y'):
    if isinstance(up_position, list) or isinstance(up_position, tuple):
        if len(up_position) != 3:
            raise IndexError('Incorrect number of position coordinates given! Must be 3 (xyz)')
        up_vector_null = tool.create_null(name='{}_UPVEC'.format(target))
    elif isinstance(up_position, str) or isinstance(up_position, unicode):
        up_vector_null = up_position
    else:
        raise Exception('Incorrect input given for parameter: up_position={}'.format(up_position))

    # Source nodes:
    sourcePMM = node.create_node('PMM', name=source + '_aimSource')
    sourceCMPM = node.create_node('CMPM', name=source + '_aimSource')

    # Target nodes:
    targetPMM = node.create_node('PMM', name=target + '_aimTarget')
    targetCMPM = node.create_node('CMPM', name=target + '_aimTarget')
    targetINVM = node.create_node('INVM', name=target + '_aimTarget')

    # Vector nodes:
    vectorMM = node.create_node('MM', name=target + '_aimVector')
    vectorDCPM = node.create_node('DCPM', name=target + '_aimVector')

    vectorNormVP = node.create_node('VP', name=target + '_normalizedAimVector')
    upVectorVP = node.create_node('VP', name=target + '_upVector')
    sideVectorVP = node.create_node('VP', name=target + '_sideVector')

    # Matrix nodes:
    compiled4x4M = node.create_node('4x4M', name=target + '_compiledVectors')
    dcpm4x4M = node.create_node('DCPM', name=target + '_compiledVectors')

    # How it works:
    # vectorNormVP gives the normalized aim vector
    #  - plug the normalized xyz into the n0, n1, n2 for desired direction
    #    * where n = [x=0, y=1, z=2]
    # upVectorVP gives normalized vector crossProduct'd with the axis direction (null/obj)
    #  - plug upVec into n0, n1, n2 for desired direction (see above)
    # sideVectorVP gives the vector for the leftover plane of rotation
    #  - plug sideVec into whichever vector is still available in the 4x4 (3x3) matrix node
    # Resulting matrix gives only rotations, aiming the target at the source

    # Source connections:
    cmds.connectAttr(source + '.t', sourcePMM + '.inPoint')
    cmds.connectAttr(source + '.parentMatrix[0]', sourcePMM + '.inMatrix')
    cmds.connectAttr(sourcePMM + '.output', sourceCMPM + '.inputTranslate')
    cmds.connectAttr(sourceCMPM + '.outputMatrix', vectorMM + '.matrixIn[0]')

    # Target connections:
    cmds.connectAttr(target + '.t', targetPMM + '.inPoint')
    cmds.connectAttr(target + '.parentMatrix[0]', targetPMM + '.inMatrix')
    cmds.connectAttr(targetPMM + '.output', targetCMPM + '.inputTranslate')
    cmds.connectAttr(targetCMPM + '.outputMatrix', targetINVM + '.inputMatrix')
    cmds.connectAttr(targetINVM + '.outputMatrix', vectorMM + '.matrixIn[1]')

    cmds.connectAttr(vectorMM + '.matrixSum', vectorDCPM + '.inputMatrix')
    cmds.connectAttr(vectorDCPM + '.outputTranslate', vectorNormVP + '.input1')

    # Assigning which vectors to assign to the 4x4 matrix plugs
    vector2directionPlugs = {
        'x': 0,
        'y': 1,
        'z': 2
    }
    compiled4x4Plugs = ['{}0', '{}1', '{}2']
    aimPlugs = lambda axis: [plug.format(vector2directionPlugs[axis]) for plug in compiled4x4Plugs]

    # Retrieve the unused axis to apply as the side axis
    axes = ['x', 'y', 'z']
    for used in (aim_vector, up_vector):
        axes.remove(used)

    aimDirectionPlugs = aimPlugs(aim_vector)    # Default X
    upDirectionPlugs = aimPlugs(up_vector)      # Default Y
    sideDirectionPlugs = aimPlugs(axes[0])      # Default Z

    # Normalized vector
    cmds.setAttr(vectorNormVP + '.operation', 0)  # no operation
    cmds.setAttr(vectorNormVP + '.normalizeOutput', 1)

    # Up vector
    cmds.setAttr(vectorNormVP + '.operation', 2)  # cross product
    cmds.setAttr(vectorNormVP + '.normalizeOutput', 0)
    cmds.connectAttr(vectorNormVP + '.output', upVectorVP + '.input1')
    cmds.connectAttr(up_vector_null + '.t', upVectorVP + '.input2')

    # Side vector
    cmds.setAttr(vectorNormVP + '.operation', 2)  # cross product
    cmds.setAttr(vectorNormVP + '.normalizeOutput', 0)
    cmds.connectAttr(upVectorVP + '.output', sideVectorVP + '.input1')
    cmds.connectAttr(vectorNormVP + '.output', sideVectorVP + '.input2')

    vectorOuts = ('outputX', 'outputY', 'outputZ')
    for output, plug in zip(vectorOuts, aimDirectionPlugs):
        cmds.connectAttr('{}.{}'.format(vectorNormVP, output), '{}.in{}'.format(compiled4x4M, plug))

    for output, plug in zip(vectorOuts, upDirectionPlugs):
        cmds.connectAttr('{}.{}'.format(upVectorVP, output), '{}.in{}'.format(compiled4x4M, plug))

    for output, plug in zip(vectorOuts, sideDirectionPlugs):
        cmds.connectAttr('{}.{}'.format(sideVectorVP, output), '{}.in{}'.format(compiled4x4M, plug))

    cmds.connectAttr(compiled4x4M + '.output', dcpm4x4M + '.inputMatrix')
    cmds.connectAttr(dcpm4x4M + '.outputRotate', target + '.r')


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

    decompose_node = node.create_node(
        node_key='DCPM',
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


# Complete beta, no applicable testing, might be rewritten entirely
def matrix_constraint(position=True, orientation=True, scale=False):

    source, inverse, target = nUtils.get_selection_list()

    mult_matrix_node = node.create_node(
        node_key='MM',
        name=source)

    decompose_node = node.create_node(
        node_key='DCPM',
        name=source)

    cmds.connectAttr(source + '.worldMatrix[0]', mult_matrix_node + '.matrixIn[0]', f=True)
    cmds.connectAttr(inverse + '.worldInverseMatrix[0]', mult_matrix_node + '.matrixIn[1]', f=True)
    cmds.connectAttr(mult_matrix_node + '.matrixSum', decompose_node + '.inputMatrix', f=True)

    if position:
        cmds.connectAttr(decompose_node + '.outputTranslate', target + '.t')
    if orientation:
        cmds.connectAttr(decompose_node + '.outputRotate', target + '.r')
    if scale:
        cmds.connectAttr(decompose_node + '.outputScale', target + '.s')


def get_index_from_component(component):
    if not len(component.split('.')) >= 2:
        raise IndexError('{} is not a component object name!'.format(component))
    return int(component.split('[')[-1][:-1])


def create_rivet(input_edges, target=None, name=''):
    if len(input_edges) != 2:
        raise IndexError('Incorrect edge count given: Must input 2 edges.')

    name = name or 'rivet_01'

    name_check = [obj.split('.')[0] for obj in input_edges]
    if name_check[0] != name_check[1]:
        raise NameError('More than one object specified for rivet!')
    full_name = name_check[0]
    input_object = name_check[0].split(':')[-1]  # no namespaces

    edge_loft = node.create_node('loft', name='{obj}_{name}_edgeLoft'.format(
        obj=input_object,
        name=name))

    i = 0
    for edge in input_edges:
        index = get_index_from_component(edge)
        edge_node = node.create_node(
            'curveFromMeshEdge',
            name='{obj}_edge_{id}'.format(obj=input_object, id=index))
        cmds.connectAttr(edge_node + '.outputCurve', edge_loft + '.inputCurve[{:04}]'.format(i))
        cmds.connectAttr(full_name + '.worldMesh[0]', edge_node + '.inputMesh')
        cmds.setAttr(edge_node + '.edgeIndex[0]', index)
        i += 1

    rivet_posi = node.create_node('POSI', name='{obj}_{name}_loftPoint'.format(
        obj=input_object,
        name=name))
    cmds.setAttr(rivet_posi + '.turnOnPercentage', 1)
    cmds.setAttr(rivet_posi + '.parameterU', 0.5)
    cmds.setAttr(rivet_posi + '.parameterV', 0.5)
    cmds.connectAttr(edge_loft + '.outputSurface', rivet_posi + '.inputSurface')
    if not target:
        target = cmds.spaceLocator(name=name + '_RIVET')[0]
        crv.set_control_color(rgb_input='yellow', input_object=target)
    cmds.connectAttr(rivet_posi + '.result.position', target + '.t')


def create_pv_guide(ik_base, ik_pivot, ik_end):
    # Naming Conventions
    parts = ik_base.split('_')
    component = parts[0]
    side = parts[1]
    # ik_joints = ensure_list(ik_joints)
    hierarchy_node = nUtils.create_transform(name='{component}_{side}_PVsolver_GRP'.format(component=component, side=side))

    start_to_end = cmds.spaceLocator(
        name='{component}_{side}_start2end_AIM'.format(component=component, side=side))
    aim_at_pole = cmds.spaceLocator(
        name='{component}_{side}_aimAtPole_AIM'.format(component=component, side=side))

    cmds.parent(aim_at_pole, start_to_end)
    cmds.select(clear=True)
    pos_crv = crv.add_curve_shape('arrow', shape_offset=(0, 90, 0), color='yellow')
    pos_arrow = nUtils.get_parent(pos_crv)
    pos_arrow = cmds.rename(pos_arrow, '{component}_{side}_defaultPV_POS'.format(component=component, side=side))
    cmds.parent(pos_arrow, aim_at_pole)

    cmds.pointConstraint(ik_base, start_to_end, maintainOffset=False)
    cmds.aimConstraint(ik_end, start_to_end, maintainOffset=False, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType='vector')
    cmds.pointConstraint(ik_pivot, aim_at_pole, maintainOffset=False, skip=['y', 'z'])
    cmds.aimConstraint(ik_pivot, aim_at_pole, maintainOffset=False, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType='vector')

    dist = nUtils.get_distance_between(ik_base, ik_end)
    norm_dist = dist / 2.0
    cmds.xform(pos_arrow, translation=[norm_dist, 0, 0], relative=True)

    cmds.parent(start_to_end, hierarchy_node)


class RivetWidget(QtWidgets.QFrame):

    enabled = 'background-color : rgb(37, 38, 40);'
    disabled = 'background-color : rgb(57, 58, 60);'

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
        object_name_layout = QtWidgets.QHBoxLayout()
        new_rivet_layout = QtWidgets.QHBoxLayout()
        rivet_button_layout = QtWidgets.QHBoxLayout()

        transform_widget.layout().addLayout(instruction_layout)
        transform_widget.layout().addLayout(object_name_layout)
        transform_widget.layout().addLayout(new_rivet_layout)
        transform_widget.layout().addLayout(rivet_button_layout)

        # Instructions -------------------------------------------------#
        instructions = QtWidgets.QLabel(
            'Input target object name, then select 2 edges to rivet between.'
        )
        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        instruction_layout.addWidget(instructions)
        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        # Object Name Field --------------------------------------------#
        rivet_object_label = QtWidgets.QLabel('Target Object Name:')
        self.rivet_object_line_edit = QtWidgets.QLineEdit()
        self.rivet_object_line_edit.setEnabled(False)
        self.rivet_object_line_edit.setStyleSheet(self.disabled)

        object_name_layout.addWidget(rivet_object_label)
        object_name_layout.addWidget(self.rivet_object_line_edit)

        # New Rivet Options---------------------------------------------#
        self.rivet_target_checkbox = QtWidgets.QCheckBox('Create New Rivet Object')
        self.rivet_target_checkbox.setChecked(True)

        new_rivet_layout.addWidget(self.rivet_target_checkbox)
        new_rivet_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        rivet_name_label = QtWidgets.QLabel('New Rivet Name:')
        self.rivet_name_line_edit = QtWidgets.QLineEdit()
        self.rivet_name_line_edit.setMinimumWidth(150)
        new_rivet_layout.addWidget(rivet_name_label)
        new_rivet_layout.addWidget(self.rivet_name_line_edit)

        # Rivet Button -------------------------------------------------#
        rivet_button_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        self.create_rivet_button = QtWidgets.QPushButton('Create Rivet')
        rivet_button_layout.addWidget(self.create_rivet_button)

        self.rivet_target_checkbox.stateChanged.connect(self._update_override_enable)
        self.create_rivet_button.clicked.connect(self.create_rivet)

    def create_rivet(self):
        # get target from textfield
        # select 2 edges
        target_name = None
        rivet_name = ''
        if self.rivet_object_line_edit.isEnabled():
            target_name = str(self.rivet_object_line_edit.text()).strip()
            if not cmds.objExists(target_name):
                raise NameError('Given name is not a node in the scene!')
        else:
            rivet_name = str(self.rivet_name_line_edit.text()).strip()

        edges = cmds.ls(selection=True, flatten=True)

        create_rivet(input_edges=edges, target=target_name, name=rivet_name)

    def _update_override_enable(self):
        value = self.rivet_target_checkbox.checkState()
        self.rivet_object_line_edit.setEnabled(not(value))
        self.rivet_name_line_edit.setEnabled(value)

        if not value:
            self.rivet_object_line_edit.setStyleSheet(self.enabled)
            self.rivet_name_line_edit.setStyleSheet(self.disabled)
        else:
            self.rivet_object_line_edit.setStyleSheet(self.disabled)
            self.rivet_name_line_edit.setStyleSheet(self.enabled)


class ConstraintWidget(mayaFrameWidget.MayaFrameWidget):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        constrain_widget = QtWidgets.QWidget()
        constrain_widget.setLayout(QtWidgets.QVBoxLayout())
        constrain_widget.layout().setContentsMargins(2, 2, 2, 2)
        constrain_widget.layout().setSpacing(5)
        constrain_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                       QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(constrain_widget)

        button_layout = QtWidgets.QHBoxLayout()
        srt_layout = QtWidgets.QHBoxLayout()

        constrain_widget.layout().addLayout(button_layout)
        constrain_widget.layout().addLayout(srt_layout)

        # Buttons ------------------------------------------------------#
        self.matrix_constrain_button = QtWidgets.QPushButton('Matrix Connection')

        button_layout.addWidget(self.matrix_constrain_button)
        # button_layout.addSpacerItem(
        #     QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        # )
        # TODO: any other relevant buttons...

        # Checkboxes ---------------------------------------------------#

        self.translate_checkbox = QtWidgets.QCheckBox('Translate')
        self.translate_checkbox.setChecked(True)
        self.rotate_checkbox = QtWidgets.QCheckBox('Rotate')
        self.rotate_checkbox.setChecked(True)
        self.scale_checkbox = QtWidgets.QCheckBox('Scale')
        self.scale_checkbox.setChecked(False)

        srt_layout.addWidget(self.translate_checkbox)
        srt_layout.addWidget(self.rotate_checkbox)
        srt_layout.addWidget(self.scale_checkbox)
        # srt_layout.addSpacerItem(
        #     QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        # )

        # Connections --------------------------------------------------#
        self.matrix_constrain_button.clicked.connect(self.matrix_constrain)

    def matrix_constrain(self):
        t = self.translate_checkbox.checkState()
        r = self.rotate_checkbox.checkState()
        s = self.scale_checkbox.checkState()

        matrix_constraint(position=t, orientation=r, scale=s)


class VectorWidget(QtWidgets.QFrame):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        vector_widget = QtWidgets.QWidget()
        vector_widget.setLayout(QtWidgets.QVBoxLayout())
        vector_widget.layout().setContentsMargins(2, 2, 2, 2)
        vector_widget.layout().setSpacing(5)
        vector_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                    QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(vector_widget)

        source_layout = QtWidgets.QHBoxLayout()
        target_layout = QtWidgets.QHBoxLayout()
        up_vector_layout = QtWidgets.QHBoxLayout()
        axes_layout = QtWidgets.QHBoxLayout()

        vector_widget.layout().addLayout(source_layout)
        vector_widget.layout().addLayout(target_layout)
        vector_widget.layout().addLayout(up_vector_layout)
        vector_widget.layout().addLayout(axes_layout)

        # Source -------------------------------------------------------#
        source_label = QtWidgets.QLabel('Source object:')

        self.source_line_edit = QtWidgets.QLineEdit()
        self.source_line_edit.setMinimumWidth(250)

        source_layout.addWidget(source_label)
        source_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        source_layout.addWidget(self.source_line_edit)

        # Target -------------------------------------------------------#
        target_label = QtWidgets.QLabel('Target object:')

        self.target_line_edit = QtWidgets.QLineEdit()
        self.target_line_edit.setMinimumWidth(250)

        target_layout.addWidget(target_label)
        target_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        target_layout.addWidget(self.target_line_edit)

        # Up Vector ----------------------------------------------------#
        up_vector_label = QtWidgets.QLabel('Up Vector object/values:')

        self.up_vector_line_edit = QtWidgets.QLineEdit()
        self.up_vector_line_edit.setMinimumWidth(250)

        up_vector_layout.addWidget(up_vector_label)
        up_vector_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        up_vector_layout.addWidget(self.up_vector_line_edit)

        # Axes/Button --------------------------------------------------#
        axes = ('x', 'y', 'z')
        aim_vector_axis_label = QtWidgets.QLabel('Aim Vector:')
        self.aim_vector_axis_combo = QtWidgets.QComboBox()
        self.aim_vector_axis_combo.addItems(axes)
        self.aim_vector_axis_combo.setCurrentIndex(0)

        up_vector_axis_label = QtWidgets.QLabel('Up Vector:')
        self.up_vector_axis_combo = QtWidgets.QComboBox()
        self.up_vector_axis_combo.addItems(axes)
        self.up_vector_axis_combo.setCurrentIndex(1)

        self.create_constraint_button = QtWidgets.QPushButton('Create Vec Aim Constraint')

        axes_layout.addWidget(aim_vector_axis_label)
        axes_layout.addWidget(self.aim_vector_axis_combo)
        axes_layout.addWidget(up_vector_axis_label)
        axes_layout.addWidget(self.up_vector_axis_combo)
        axes_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        axes_layout.addWidget(self.create_constraint_button)

        # Connections --------------------------------------------------#
        self.create_constraint_button.clicked.connect(self.create_vector_aim_constraint)

    def create_vector_aim_constraint(self):
        source = str(self.source_line_edit.text()).strip()
        target = str(self.target_line_edit.text()).strip()
        up_vec_text = self.up_vector_line_edit.text().strip()
        try:
            int(up_vec_text[0])
            up_vector = list(up_vec_text)
        except:
            up_vector = str(self.up_vector_line_edit.text())
        aim_axis = self.aim_vector_axis_combo.currentText()
        up_vector_axis = self.up_vector_axis_combo.currentText()

        vector_aim_constraint(
            source=source,
            target=target,
            up_position=up_vector,
            aim_vector=aim_axis,
            up_vector=up_vector_axis)


class PVWidget(mayaFrameWidget.MayaFrameWidget):

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
        ik_start_layout = QtWidgets.QHBoxLayout()
        ik_pivot_layout = QtWidgets.QHBoxLayout()
        ik_end_layout = QtWidgets.QHBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()

        transform_widget.layout().addLayout(instruction_layout)
        transform_widget.layout().addLayout(ik_start_layout)
        transform_widget.layout().addLayout(ik_pivot_layout)
        transform_widget.layout().addLayout(ik_end_layout)
        transform_widget.layout().addLayout(button_layout)

        # Instructions -------------------------------------------------#
        instructions = QtWidgets.QLabel(
            'Creates a pole vector solver between the given joints.'
        )
        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        instruction_layout.addWidget(instructions)
        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        # IK Start Joint Field --------------------------------------------#
        ik_start_label = QtWidgets.QLabel('IK Base Joint:')
        self.ik_start_line_edit = QtWidgets.QLineEdit('')

        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        ik_start_label.setFixedWidth(80)

        ik_start_layout.addWidget(ik_start_label)
        ik_start_layout.addWidget(self.ik_start_line_edit)

        # IK Pivot Joint Field --------------------------------------------#
        ik_pivot_label = QtWidgets.QLabel('IK Pivot Joint:')
        self.ik_pivot_line_edit = QtWidgets.QLineEdit('')

        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        ik_pivot_label.setFixedWidth(80)

        ik_pivot_layout.addWidget(ik_pivot_label)
        ik_pivot_layout.addWidget(self.ik_pivot_line_edit)

        # IK End Joint Field --------------------------------------------#
        ik_end_label = QtWidgets.QLabel('IK End Joint:')
        self.ik_end_line_edit = QtWidgets.QLineEdit('')

        instruction_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )

        ik_end_label.setFixedWidth(80)

        ik_end_layout.addWidget(ik_end_label)
        ik_end_layout.addWidget(self.ik_end_line_edit)

        # Rivet Button -------------------------------------------------#
        button_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        self.create_pv_solver_button = QtWidgets.QPushButton('Create PV Solver')
        button_layout.addWidget(self.create_pv_solver_button)

        self.create_pv_solver_button.clicked.connect(self.create_pv_solver)

    def create_pv_solver(self):
        ik_start = str(self.ik_start_line_edit.text()).strip()
        ik_pivot = str(self.ik_pivot_line_edit.text()).strip()
        ik_end = str(self.ik_end_line_edit.text()).strip()

        invalid_objects = [obj for obj in (ik_start, ik_pivot, ik_end) if not cmds.objExists(obj)]

        if invalid_objects:
            return self.popUpError(
                NameError('No object matches name(s): {}'.format(str(invalid_objects))))

        create_pv_guide(ik_base=ik_start, ik_pivot=ik_pivot, ik_end=ik_end)
