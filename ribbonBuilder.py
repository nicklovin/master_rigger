import maya.cmds as cmds
from master_rigger import basicTools as tool
from master_rigger import curve_assignment as crv


def build_ribbon_plane(span_count, length_ratio=None, ribbon_name='C_ribbon'):
    
    # input number of joints desired to use
    width = float(span_count)
    if not length_ratio:
        length_ratio = 1/width
    
    cmds.nurbsPlane(ax=[0, 1, 0], w=width, lr=length_ratio, d=3, u=span_count,
                    v=1, ch=0, n=ribbon_name + '_SRF')


def build_ribbon(object_input=None, span_align='face', override_ctrls=True,
                 prefix='C', ribbon_name='ribbon'):
    
    if not object_input:
        try:
            object_input = cmds.ls(selection=True)[0]
        except IndexError:
            cmds.warning('No selection or object_input assigned!  Please select'
                         ' an object or input a name into the parameter.')
            return

    u_spans = cmds.getAttr(object_input + '.su')

    if span_align == 'face':
        u_factor = u_spans
        u_offset = 1.0 / (2 * u_spans)
    elif span_align == 'edge':
        u_factor = u_spans + 1
        u_offset = 0
    else:
        cmds.error('Incorrect value given to parameter span_align!  Retry with '
                   'either "face" or "edge".')
        return

    follicle_grp = cmds.group(empty=True, name='%s_%s_follicle_GRP' %
                                               (prefix, ribbon_name))

    bone_list = []
    for span in range(u_factor):
        b = str(span+1).zfill(2)
        follicle_shape = cmds.createNode('follicle',
                                         name='%s_%s_%s_FOLShape' %
                                              (prefix, ribbon_name, b))
        follicle_parent = cmds.listRelatives(follicle_shape, parent=True)
        follicle_srt = cmds.rename(follicle_parent, '%s_%s_%s_FOL' %
                                                    (prefix, ribbon_name, b))
        
        cmds.connectAttr(object_input + '.worldMatrix[0]',
                         follicle_shape + '.inputWorldMatrix')
        cmds.connectAttr(object_input + '.local',
                         follicle_shape + '.inputSurface')
        
        cmds.connectAttr(follicle_shape + '.outRotate',
                         follicle_srt + '.rotate')
        cmds.connectAttr(follicle_shape + '.outTranslate',
                         follicle_srt + '.translate')
        
        u_value = (1.0/u_spans) * span + u_offset
        v_value = 0.5
        
        cmds.setAttr(follicle_shape + '.pu', u_value)
        cmds.setAttr(follicle_shape + '.pv', v_value)
        
        cmds.select(cl=True)

        bone_zero = cmds.group(empty=True,
                               name=follicle_srt.replace('FOL', 'BONE_ZERO'))
        follicle_bone = cmds.joint(name=follicle_srt.replace('FOL', 'BONE'),
                                   radius=0.1)
        bone_list.append(bone_zero)

        if override_ctrls:
            follicle_ctrl = cmds.group(empty=True,
                                       name=follicle_srt.replace('FOL', 'CTRL'))
            ctrl_zero = tool.create_offset(input_object=follicle_ctrl)
            crv.add_curve_shape('circle', transform_node=follicle_ctrl)

            cmds.parentConstraint(follicle_srt, ctrl_zero, mo=False)
            cmds.parentConstraint(follicle_ctrl, follicle_bone, mo=False)

        cmds.parentConstraint(follicle_srt, bone_zero, mo=False)
        cmds.parent(follicle_srt, follicle_grp)
    cmds.group(bone_list, name='%s_%s_bone_GRP' % (prefix, ribbon_name))
