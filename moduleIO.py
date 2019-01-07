import maya.cmds as cmds


attributes = ['.tx', '.ty', '.tz',
              '.rx', '.ry', '.rz',
              '.sx', '.sy', '.sz']


def limb_in_out_module(input_module, output_module):

    input_mod = input_module.replace('_MOD', '_input_MOD')
    output_mod = output_module.replace('_MOD', '_output_MOD')

    for attr in attributes:
        cmds.connectAttr(output_mod + attr, input_mod + attr)
