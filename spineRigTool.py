import maya.cmds as cmds
from MasterRigger import ribbonBuilder as ribbon
from MasterRigger import curve_assignment as crv
from MasterRigger import basicTools as tool
from MasterRigger import attributeManipulation as attr
from MasterRigger import createNodeLibrary as node

default_positions = [
    [0, 10, 0],
    [0, 11, 0],
    [0, 12, -0.25],
    [0, 13, -0.5],
    [0, 14, -0.5],
    [0, 15, -0.5]
]

spine_drivers = ['pelvis', 'hips', 'chest_IK', 'chest_FK']
spine_shapes = ['circle', 'circle', 'octagon', 'circle']
spine_driver_jnt_list = []

cog_attribute_dict = {
    'secondaryVisibility': ['bool', None, None, 0, False, None],
    'spineControlVisibility': ['bool', None, None, 0, False, None],
    'spineIKFK': ['double', 0, 1, 0, True, None],
}

spine_locator_list = []
locator_world_positions = []
ik_bind_list = []
fk_bind_list = []
ik_spine_bones = []
fk_spine_bones = []
spine_blendshape = []


def build_spine_library():
    pass


def create_spine_locators(prefix='C'):
    parent_locator = None
    for loc in range(6):
        point = cmds.spaceLocator(name='%s_spine_0%s_LOC' % (prefix, str(loc)))
        cmds.xform(point, translation=default_positions[loc], worldSpace=True)
        if parent_locator:
            cmds.parent(point, parent_locator)
        parent_locator = point
        if loc == 5:
            cmds.xform(point[0], scale=[0.25, 0.25, 0.25])
            end = cmds.rename(point[0], point[0].replace('05', 'END'))
            spine_locator_list.append(end)
            break
        spine_locator_list.append(point[0])


def build_spine_system(bind_joint_count=5, prefix='C'):
    # Creating a list of the locator positions
    end_world_position = None
    for loc in spine_locator_list:
        if 'END' in loc:
            end_world_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
            continue
        point_world_position = cmds.getAttr(loc + '.worldPosition[0]')[0]
        locator_world_positions.append(point_world_position)

    # Building Spine Curve
    spine_crv = cmds.curve(degree=3,
                           point=locator_world_positions,
                           name='%s_spine_base_CRV' % prefix)
    locator_world_positions.append(end_world_position)

    cmds.rebuildCurve(spine_crv,
                      constructionHistory=False,
                      end=True,
                      degree=3,
                      spans=bind_joint_count-1,
                      replaceOriginal=True)

    # Building Spine Ribbon
    left_duplicate_crv = cmds.duplicate(spine_crv,
                                        name='%s_lt_spine_ref_CRV' % prefix)
    # Check that these directions are correct.  Mostly irrelevant though
    cmds.xform(left_duplicate_crv, translation=[0.5, 0, 0], worldSpace=True)
    right_duplicate_crv = cmds.duplicate(spine_crv,
                                         name='%s_rt_spine_ref_CRV' % prefix)
    cmds.xform(right_duplicate_crv, translation=[-0.5, 0, 0], worldSpace=True)

    # Building the Ribbons
    spine_ribbon = cmds.loft(left_duplicate_crv, right_duplicate_crv,
                             name='%s_spine_ribbon_SRF' % prefix,
                             uniform=True,
                             constructionHistory=False,
                             polygon=0,
                             reverseSurfaceNormals=True)[0]

    cmds.group(spine_crv, left_duplicate_crv, right_duplicate_crv,
               name=prefix + '_spine_ref_CRV_GRP')

    # Ribbon blendshapes
    ik_ribbon = cmds.duplicate(spine_ribbon,
                               name=spine_ribbon.replace('SRF', 'IK_SHP'))
    fk_ribbon = cmds.duplicate(spine_ribbon,
                               name=spine_ribbon.replace('SRF', 'FK_SHP'))

    # Building the follicles and bones
    ribbon.build_ribbon(spine_ribbon,
                        span_align='edge',
                        override_ctrls=False,
                        ribbon_name='spine_ribbon')

    # Influence blendshape
    spine_shp = cmds.blendShape(fk_ribbon, ik_ribbon, spine_ribbon,
                                name=spine_ribbon.replace('SRF', 'IKFK_BSHP'))
    spine_blendshape.append(spine_shp[0])

    # Building driver joint chains
    ik_parent = None
    fk_parent = None
    ik_end = None
    fk_end = None
    driver_kill_list = []
    for jnt in range(6):
        # End joint condition
        if jnt == 5:
            cmds.select(clear=True)
            ik_jnt = cmds.joint(name='%s_spine_driver_END_IK_JNT' % prefix)
            cmds.select(clear=True)
            fk_jnt = cmds.joint(name='%s_spine_driver_END_FK_JNT' % prefix)
            cmds.xform(ik_jnt, fk_jnt,
                       translation=locator_world_positions[3],
                       worldSpace=True)
            ik_end = ik_jnt
            fk_end = fk_jnt
        # All other joint condition
        else:
            cmds.select(clear=True)
            ik_jnt = cmds.joint(name='%s_spine_driver_0%s_IK_JNT' %
                                     (prefix, str(jnt)))
            cmds.select(clear=True)
            fk_jnt = cmds.joint(name='%s_spine_driver_0%s_FK_JNT' %
                                     (prefix, str(jnt)))

            cmds.xform(ik_jnt, fk_jnt,
                       translation=locator_world_positions[jnt],
                       worldSpace=True)
            # Setting the 3rd and 4th joints to be deleted (replaced with chest)
            if jnt == 3 or jnt == 4:
                driver_kill_list.append(ik_jnt)
                driver_kill_list.append(fk_jnt)
            if jnt == 0:
                spine_driver_jnt_list.append(ik_jnt)
                spine_driver_jnt_list.append(fk_jnt)
        # Setting the parent joint from previous loop
        if ik_parent and fk_parent:
            cmds.parent(ik_jnt, ik_parent)
            cmds.parent(fk_jnt, fk_parent)
        # Avoid deleting the ends too early so that the joints can be oriented
        if ik_end and fk_end:
            cmds.parent(ik_end, ik_spine_bones[2])
            cmds.parent(fk_end, fk_spine_bones[2])
            continue
        ik_spine_bones.append(ik_jnt)
        fk_spine_bones.append(fk_jnt)
        ik_parent = ik_jnt
        fk_parent = fk_jnt

    # Building the
    for driver in spine_drivers:
        if 'chest' in driver:
            cmds.select(clear=True)
            driver_jnt = cmds.joint(
                name='%s_%s_JNT' % (prefix, driver))
            temp_cns = cmds.pointConstraint(
                '%s_spine_driver_03_IK_JNT' % prefix,
                '%s_spine_driver_04_IK_JNT' % prefix,
                driver_jnt,
                mo=False)
            cmds.delete(temp_cns)
            if 'IK' in driver:
                ik_spine_bones.append(driver_jnt)
            else:
                fk_spine_bones.append(driver_jnt)
            spine_driver_jnt_list.append(driver_jnt)
        else:
            cmds.select(clear=True)
            spine_driver = cmds.joint(name='%s_%s_JNT' % (prefix, driver))
            cmds.xform(spine_driver,
                       translation=locator_world_positions[0],
                       worldSpace=True)
            ik_spine_bones.append(spine_driver)
            fk_spine_bones.append(spine_driver)
            spine_driver_jnt_list.append(spine_driver)

    # Killing the unnecessary joints made by the loops
    i = 0
    for trash in driver_kill_list:
        if trash in ik_spine_bones:
            ik_spine_bones.remove(trash)
        i = i + 1
    for trash in driver_kill_list:
        if trash in fk_spine_bones:
            fk_spine_bones.remove(trash)
        i = i + 1

    cmds.delete(driver_kill_list)

    # Orienting the driver joints
    cmds.joint('%s_spine_driver_00_IK_JNT' % prefix,
               '%s_spine_driver_00_FK_JNT' % prefix,
               edit=True,
               orientJoint='xzy',
               secondaryAxisOrient='xup',
               children=True,
               zeroScaleOrient=True)

    cmds.delete(ik_end, fk_end)

    # Add a dropoff rate later if it makes sense
    ik_skin = cmds.skinCluster(ik_spine_bones, ik_ribbon, toSelectedBones=True)
    fk_skin = cmds.skinCluster(fk_spine_bones, fk_ribbon, toSelectedBones=True)

    # Creating a list of the objects that influence the ribbon skins
    ik_skin_connections = cmds.listConnections(ik_skin, source=True)
    for item in ik_skin_connections:
        if item in ik_bind_list:
            continue
        if 'JNT' in ik_skin_connections:
            ik_bind_list.append(item)

    fk_skin_connections = cmds.listConnections(fk_skin, source=True)
    for item in fk_skin_connections:
        if item in fk_bind_list:
            continue
        if 'JNT' in fk_skin_connections:
            fk_bind_list.append(item)

    # Add something to force even weights to the ribbon influence


def create_spine_controls(prefix='C', control_colors=('yellow', 'orange')):
    # Building a COG control to be the center of everything
    cog_scnd_ctrl = cmds.group(empty=True, name=prefix + '_COG_SCND_CTRL')
    cog_scnd_shape = crv.add_curve_shape(shape_choice='box',
                                         transform_node=cog_scnd_ctrl,
                                         color=control_colors[0],
                                         off_color=True)
    cmds.xform(cog_scnd_ctrl + '.cv[0:]', scale=[2.2, 0.6, 2.2])
    cog_ctrl = cmds.group(cog_scnd_ctrl, name=prefix + '_COG_CTRL')
    crv.add_curve_shape(shape_choice='box',
                        transform_node=cog_ctrl,
                        color=control_colors[0])
    cmds.xform(cog_ctrl + '.cv[0:]', scale=[2, 0.5, 2])
    cog_offset = tool.create_offset(input_object=cog_ctrl)
    tool.match_transformations(rotation=False,
                               source=prefix + '_pelvis_JNT',
                               target=cog_offset)
    for attribute in cog_attribute_dict:
        attr.create_attr(attribute,
                         attribute_type=cog_attribute_dict[attribute][0],
                         input_object=cog_ctrl,
                         min_value=cog_attribute_dict[attribute][1],
                         max_value=cog_attribute_dict[attribute][2],
                         default_value=cog_attribute_dict[attribute][3],
                         keyable=cog_attribute_dict[attribute][4],
                         enum_names=cog_attribute_dict[attribute][5])

    # Main body controls
    ik_vis = []
    i = 0
    for ctrl in spine_drivers:
        control = cmds.group(empty=True, name='%s_%s_CTRL' % (prefix, ctrl))
        zero = tool.create_offset(input_object=control)
        tool.create_offset(suffix='OFS', input_object=control)
        tool.match_transformations(source=control.replace('CTRL', 'JNT'),
                                   target=zero)
        if 'IK' not in ctrl:
            crv.add_curve_shape(shape_choice=spine_shapes[i],
                                transform_node=control,
                                color=control_colors[0])
        else:
            crv.add_curve_shape(shape_choice=spine_shapes[i],
                                transform_node=control,
                                color=control_colors[1])
            ik_vis.append(zero)
        cmds.parentConstraint(control, control.replace('CTRL', 'JNT'), mo=True)
        if 'chest' not in ctrl:
            cmds.parent(zero, cog_scnd_ctrl)
        i = i + 1

    ikfk_shapes_vis_list = []
    # IK spine controls
    ik_parent = prefix + '_pelvis_CTRL'
    for jnt in ik_spine_bones:
        if 'spine' not in jnt or '00' in jnt:
            continue
        ik_ctrl = cmds.group(empty=True, name=jnt.replace('JNT', 'CTRL'))
        ik_offset = tool.create_offset(input_object=ik_ctrl)
        shape = crv.add_curve_shape(shape_choice='octagon',
                                    transform_node=ik_ctrl,
                                    color=control_colors[1],
                                    shape_offset=[0, 0, 90])
        tool.match_transformations(source=jnt, target=ik_offset)
        cmds.parentConstraint(ik_ctrl, jnt, mo=False)
        cmds.parent(ik_offset, ik_parent)
        ikfk_shapes_vis_list.append(shape)
        ik_vis.append(ik_offset)
        if '02' in jnt:
            cmds.parentConstraint(ik_parent,
                                  prefix + '_chest_IK_CTRL',
                                  ik_offset,
                                  mo=True)

    # FK spine controls
    fk_ctrl = None
    fk_parent = None
    fk_vis = []
    for jnt in fk_spine_bones:
        if 'spine' not in jnt or '00' in jnt:
            continue
        fk_ctrl = cmds.group(empty=True, name=jnt.replace('JNT', 'CTRL'))
        fk_offset = tool.create_offset(input_object=fk_ctrl)
        fk_vis.append(fk_offset)
        shape = crv.add_curve_shape(shape_choice='circle',
                                    transform_node=fk_ctrl,
                                    color=control_colors[0],
                                    shape_offset=[0, 0, 90])
        tool.match_transformations(source=jnt, target=fk_offset)
        cmds.parentConstraint(fk_ctrl, jnt, mo=False)
        ikfk_shapes_vis_list.append(shape)
        if fk_parent:
            cmds.parent(fk_offset, fk_parent)
        else:
            cmds.parent(fk_offset, ik_parent)
        fk_parent = fk_ctrl

    cmds.parent(prefix + '_chest_IK_CTRL_ZERO', cog_scnd_ctrl)
    cmds.parent(prefix + '_chest_FK_CTRL_ZERO', fk_ctrl)

    cmds.connectAttr(cog_ctrl + '.secondaryVisibility', cog_scnd_shape + '.v')
    spine_rev = node.create_node(node_key='REV',
                                 name=prefix + '_spineIKFK_blend')
    cmds.connectAttr(cog_ctrl + '.spineIKFK', spine_rev + '.inputX')
    for shape in ikfk_shapes_vis_list:
        vis_factor = node.create_node(node_key='MDL', name=shape)
        cmds.connectAttr(cog_ctrl + '.spineControlVisibility',
                         vis_factor + '.input1')
        if 'FK' not in shape:
            # IK vis
            cmds.connectAttr(cog_ctrl + '.spineIKFK', vis_factor + '.input2')
        else:
            # FK vis
            cmds.connectAttr(spine_rev + '.outputX', vis_factor + '.input2')
        cmds.connectAttr(vis_factor + '.output', shape + '.v')

    cmds.connectAttr(spine_rev + '.outputX',
                     '%s_%s_CTRLShape.v' % (prefix, spine_drivers[3]))
    cmds.connectAttr(cog_ctrl + '.spineIKFK',
                     '%s_%s_CTRLShape.v' % (prefix, spine_drivers[2]))

    # In blendshape node, weight[0] is FK and weight[1] is IK
    cmds.connectAttr(spine_rev + '.outputX', spine_blendshape[0] + '.weight[0]')
    cmds.connectAttr(cog_ctrl + '.spineIKFK', spine_blendshape[0] + '.weight[1]')

    cmds.group(spine_driver_jnt_list, name=prefix + '_spine_driver_JNT_GRP')
