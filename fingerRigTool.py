import maya.cmds as cmds
import pprint
from string import ascii_uppercase
from master_rigger import curve_assignment as crv
from master_rigger import attributeManipulation as attr
from master_rigger import createNodeLibrary as node
from master_rigger import basicTools as tool
reload(crv)
reload(attr)
reload(node)
reload(tool)


class HandModule(object):

    # Letters for finger enumeration
    LETTERS_INDEX = {index: letter for index, letter in
                     enumerate(ascii_uppercase, start=1)}
    # Dictionary variable, used for all callbacks and built with first function
    fingers_dict = {}

    hand_control = ''
    hand_parent = ''

    def __init__(self, side, finger_count, segment_count, thumb=True, **kwargs):
        self.side = side
        self.finger_count = finger_count
        self.segment_count = segment_count
        self.thumb = thumb
        self.shape_type = kwargs.get('shape_type', 'box')
        self.limit_attrs = kwargs.get('limit_attrs', True)
        self.hand_shape = kwargs.get('hand_shape', 'triangle')
        self.metacarpus = kwargs.get('metacarpus', False)
        self.inverse = -1 if kwargs.get('inverse', False) else 1

        self.build_finger_library()

    def __str__(self):
        flattened_dict = pprint.pformat(self.fingers_dict)
        return 'HandModule(\n' + flattened_dict + '\n)'

    def _autoBuild(self):
        """ For Testing purposes only
        """
        self.create_finger_locators()
        self.create_finger_joints()
        self.create_finger_controls()
        self.connect_fingers()

    def build_hand_module(self):
        # For full-scale auto rigging only
        pass

    def build_finger_library(self):
        """
        Builds a dictionary (library) of all the parts of the hand/fingers based on
        the inputs to suit individualized characters not limited to human hand
        features.

        Args:
            finger_count (int): The number of fingers being created, thumb excluded.
            thumb (bool): If building a thumb is needed.
            segment_count (int): the number of finger segments in each finger.
            side (str): Body orientation of the fingers.
                'L/M/R' are appropriate inputs.

        Returns:
            self.fingers_dict (dictionary): Dictionary with each finger as a key, giving
                a list for the segments of the given finger key.

        """
        metacarpus = 1 if self.metacarpus else 0

        for finger in range(self.finger_count):
            finger = finger + 1
            finger_letter = self.LETTERS_INDEX[finger]
            finger_key = 'Hand_{side}_finger{index}'.format(side=self.side, index=finger_letter)
            finger_segment_list = []
            for segment in range(self.segment_count + 1 + metacarpus):
                if segment >= (self.segment_count + metacarpus):
                    segment = 'END'
                else:
                    segment = '{:02}'.format(segment + 1 - metacarpus)

                finger_segment_list.append('Hand_{side}_finger{index}_{segment}'.format(
                                           side=self.side,
                                           index=finger_letter,
                                           segment=segment))
            self.fingers_dict[finger_key] = finger_segment_list

        if self.thumb:
            thumb_segment_list = []
            thumb_key = 'Hand_{}_thumb'.format(self.side)
            for segment in range(self.segment_count + 1):
                if segment >= self.segment_count:
                    segment = 'END'
                else:
                    segment = '{:02}'.format(segment + 1)

                thumb_segment_list.append('Hand_%s_thumb_%s'
                                          % (self.side, segment))
            self.fingers_dict[thumb_key] = thumb_segment_list

        return self.fingers_dict

    def create_finger_locators(self):
        """
        Creates the locators for the finger position alignments.

        Args:
            side (str): Body orientation of the fingers.
                'L/M/R' are appropriate inputs.

        """
        self.hand_parent = cmds.spaceLocator(name='Hand_{side}_handBase_POS'.format(side=self.side))[0]
        for finger, segments in self.fingers_dict.iteritems():
            for segment in segments:
                cmds.spaceLocator(name='{segment}_POS'.format(side=self.side, segment=segment))
            # Parenting logic
            for loc in range(len(segments)):
                if loc == (len(segments) - 1):
                    cmds.parent(segments[0] + '_POS', self.hand_parent)
                else:
                    cmds.parent(segments[loc + 1] + '_POS',
                                segments[loc] + '_POS')

        cmds.setAttr(self.hand_parent + '.overrideEnabled', 1)
        cmds.setAttr(self.hand_parent + '.overrideColor', 13)

        i = (len(self.fingers_dict) / 2) - 1
        for key in sorted(self.fingers_dict.keys()):
            for segment in self.fingers_dict[key]:
                cmds.move(1, 0, 0, segment + '_POS', relative=True)
            cmds.move(1, 0, i, self.fingers_dict[key][0] + '_POS', relative=True)
            if 'thumb' in key:
                cmds.rotate(0, -45, 0, self.fingers_dict[key][0] + '_POS', relative=True)
                cmds.move(-1, 0, len(self.fingers_dict), self.fingers_dict[key][0] + '_POS',
                          relative=True)
            i -= 1

    def create_finger_joints(self):
        """
        Creates the joints for the finger.

        Args:
            side (str): Body orientation of the fingers.
                'L/M/R' are appropriate inputs.

        """
        finger_start_list = []
        cmds.select(clear=True)
        hand_joint = cmds.joint(name='Hand_{}_handBase_BONE'.format(self.side))
        tool.match_transformations(source=self.hand_parent, target=hand_joint)
        cmds.xform(self.hand_parent, query=True, rotation=True, relative=True)
        hand_orientation = [val for val in cmds.xform(self.hand_parent, query=True, rotation=True, relative=True)]
        cmds.setAttr(hand_joint + '.r', 0, 0, 0)
        cmds.setAttr(hand_joint + '.jointOrient', hand_orientation[0], hand_orientation[1] * self.inverse, hand_orientation[2] * self.inverse)
        for _, segments in sorted(self.fingers_dict.iteritems()):
            cmds.select(clear=True)
            for segment in segments:
                print segment
                locator_position = cmds.getAttr(segment + '_POS.worldPosition[0]')[0]
                finger_joint = cmds.joint(name=segment + '_BONE',
                                          position=[locator_position[0],
                                                    locator_position[1],
                                                    locator_position[2]])
                if 'thumb_01' in segment or segment.endswith('00'):
                    print 'adding {} to finger_start_list'.format(finger_joint)
                    finger_start_list.append(finger_joint)

        cmds.parent(finger_start_list, hand_joint)

        for _, segments in sorted(self.fingers_dict.iteritems()):
            for segment in segments:
                locator_reference = segment + '_POS'
                joint_reference = segment + '_BONE'
                locator_position = cmds.getAttr(locator_reference
                                                + '.worldPosition[0]')[0]
                locator_rotations = cmds.getAttr(locator_reference + '.r')[0]
                cmds.setAttr(joint_reference + '.jointOrientX',
                             locator_rotations[0])
                cmds.setAttr(joint_reference + '.jointOrientY',
                             locator_rotations[1] * self.inverse)
                cmds.setAttr(joint_reference + '.jointOrientZ',
                             locator_rotations[2] * self.inverse)
                cmds.joint(joint_reference,
                           edit=True,
                           position=[locator_position[0],
                                     locator_position[1],
                                     locator_position[2]])

    def create_finger_controls(self):
        """
        Creates controls for the joints of the finger.

        Args:
            shape_type (str): Assigns the control shape type for the individual
                finger controls.  Options vary based on the curve_assignment
                availability (must be imported properly to function).
            offset (bool): Allow for an additional offset group to be added to the
                control chain (can be used for gimbal, set-driven keys, etc.)
            limit_attrs (bool): Automatically lock attributes on segments, limiting
                controls to rotateZ.
            self.hand_control (bool): Create a single control to override/blend with the
                individual controls on the finger.  By default, will also contain
                attributes for IKFK and other useful tools.  True by default.
            side (str): Body orientation of the fingers.
                'L/M/R' are appropriate inputs.

        """
        attr_names = []

        for key, segments in sorted(self.fingers_dict.iteritems()):
            # Declaring the parent variable before it gets continually reassigned
            parent_curve = None
            for segment in segments:
                if segment.endswith('END'):
                    continue
                elif segment.endswith('00'):
                    finger_ctrl = None
                    finger_srt = cmds.group(empty=True, n=segment + '_SRT')
                    finger_ofs = cmds.group(finger_srt, n=segment + '_OFS')
                    segment_position = cmds.xform(segment + '_BONE',
                                                  query=True,
                                                  translation=True,
                                                  worldSpace=True)
                    segment_orientation = cmds.xform(segment + '_BONE',
                                                     query=True,
                                                     rotation=True,
                                                     worldSpace=True)
                    cmds.setAttr(finger_ofs + '.t', segment_position[0], segment_position[1], segment_position[2])
                    cmds.setAttr(finger_ofs + '.r', segment_orientation[0], segment_orientation[1], segment_orientation[2])

                else:
                    # Convert to basicTools.create_offset() or .create_hierarchy()
                    finger_ctrl = cmds.group(empty=True, n=segment + '_CTL')
                    crv.add_curve_shape(shape_choice=self.shape_type,
                                        transform_node=finger_ctrl)
                    finger_srt = cmds.group(finger_ctrl, n=segment + '_SRT')
                    # if offset:
                    #     finger_ofs = cmds.group(finger_srt, n=segment + '_OFS')
                    #     finger_zero = cmds.group(finger_ofs, n=segment + '_ZERO')
                    # else:
                    if True:  # Rewrite nicer later
                        finger_ofs = cmds.group(finger_srt, n=segment + '_OFS')
                    segment_position = cmds.xform(segment + '_BONE',
                                                  query=True,
                                                  translation=True,
                                                  worldSpace=True)
                    segment_orientation = cmds.xform(segment + '_BONE',
                                                     query=True,
                                                     rotation=True,
                                                     worldSpace=True)
                    cmds.setAttr(finger_ofs + '.t', segment_position[0], segment_position[1], segment_position[2])
                    cmds.setAttr(finger_ofs + '.r', segment_orientation[0], segment_orientation[1], segment_orientation[2])

                # If the control group is not the base of the finger, parent
                if '00' not in segment:
                    if parent_curve:
                        cmds.parent(finger_ofs, parent_curve)
                    # Lock unnecessary attributes if assigned
                    if self.limit_attrs:
                        attr.lock_hide(1, 1, 1, 0, 0, 0, 1, 1, 1, 1,
                                       objects=[finger_ctrl])
                parent_curve = finger_ctrl or finger_srt  # if '00' joint

                if not segment.endswith(('END', '00')):
                    attr_name = '_'.join(segment.split('_')[2:])
                    attr_names.append(attr_name)

            # Must be repeated later to avoid overcorrecting the looping list
            for segment in segments:
                if segment.endswith('00'):
                    segments.remove(segment)
                    self.fingers_dict[key] = segments
                    break

        hand_control = cmds.group(empty=True, name='Hand_{side}_handBase_CTL'.format(side=self.side))
        crv.add_curve_shape(shape_choice=self.hand_shape,
                            transform_node=hand_control)
        hand_position = cmds.xform(hand_control.replace('CTL', 'BONE'),
                                   query=True,
                                   translation=True,
                                   worldSpace=True)
        hand_orientation = cmds.xform(hand_control.replace('CTL', 'BONE'),
                                      query=True,
                                      rotation=True,
                                      worldSpace=True)

        cmds.setAttr(hand_control + '.t', hand_position[0], hand_position[1], hand_position[2])
        cmds.setAttr(hand_control + '.r', hand_orientation[0], hand_orientation[1], hand_orientation[2])

        attr.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                       objects=[hand_control])

        attr.create_attr(attribute_name='IKFK',
                         attribute_type='double',
                         input_object=hand_control,
                         min_value=0, max_value=1, default_value=1)
        attr.create_attr(attribute_name='spread',
                         attribute_type='double',
                         input_object=hand_control,
                         min_value=-10, max_value=10)
        attr.create_attr(attribute_name='masterRotation',
                         attribute_type='double',
                         input_object=hand_control)
        attr.create_attr(attribute_name='offset',
                         attribute_type='double',
                         input_object=hand_control)
        attr.create_attr(attribute_name='offsetFavor',
                         attribute_type='enum',
                         input_object=hand_control, default_value=1,
                         enum_names=['Inner', 'Outer'])

        for attribute in sorted(attr_names):
            attr.create_attr(attribute_name=attribute,
                             attribute_type='double',
                             input_object=hand_control)

        for key in sorted(self.fingers_dict.keys()):
            vis_attribute = key.split('_')[-1] + '_Vis'
            attr.create_attr(attribute_name=vis_attribute,
                             attribute_type='bool',
                             input_object=hand_control, default_value=1)

        self.hand_control = hand_control

    def connect_fingers(self):
        """
        Creates necessary connections for the fingers, and applies them to the hand
        control if applicable.

        Args:
            self.hand_control (str): Assign name of the hand control created in the previous
                step.  If used with interface, should be automatically assigned.  If
                using commands separately, set manually.
            side (str): Body orientation of the fingers.
                'L/M/R' are appropriate inputs.

        """
        # Declaring early repeating factors
        offset_attr_factor = 0
        reverse_attr_factor = len(self.fingers_dict) - 2  # accounts for no thumb offset

        for finger, segments in sorted(self.fingers_dict.iteritems()):
            print finger, segments
            # Building the node network
            if self.hand_control:
                # Visibility connections
                cmds.connectAttr('%s.%s_Vis' % (self.hand_control, finger.split('_')[-1]),
                                 finger + '_01_OFS.v')
                # Remove the thumb from the automations
                if 'thumb' not in finger:
                    finger_srt_mult = node.create_node('MDIV', name=finger)
                    finger_srt_cnd = node.create_node('CND', name=finger)

                    cmds.setAttr(finger_srt_cnd + '.colorIfFalseR',
                                 reverse_attr_factor)
                    cmds.setAttr(finger_srt_cnd + '.colorIfTrueR',
                                 offset_attr_factor)
                    cmds.setAttr(finger_srt_cnd + '.secondTerm', 0)
                    cmds.setAttr(finger_srt_cnd + '.operation', 1)

                    cmds.connectAttr(finger_srt_cnd + '.outColorR',
                                     finger_srt_mult + '.input2X')
                    cmds.connectAttr(self.hand_control + '.offsetFavor',
                                     finger_srt_cnd + '.firstTerm')
                    cmds.connectAttr(self.hand_control + '.offset',
                                     finger_srt_mult + '.input1X')

            # Creating the initial segment constraints
            for segment in segments:
                if 'END' in segment:
                    continue
                ctrl = segment + '_CTL'
                bone = segment + '_BONE'
                cmds.parentConstraint(ctrl, bone, mo=True)

                # Building the SRT values network, if applicable
                if self.hand_control:
                    finger_attr = '_'.join(segment.split('_')[2:])
                    finger_srt_sum = node.create_node('PMA', name=segment)
                    finger_inverse_mdl = node.create_node('MDL', name=segment + '_inverse')
                    cmds.setAttr(finger_inverse_mdl + '.input2', self.inverse)
                    if 'thumb' in segment:
                        cmds.connectAttr(self.hand_control + '.' + finger_attr,
                                         finger_inverse_mdl + '.input1')
                        cmds.connectAttr(finger_inverse_mdl + '.output',
                                         segment + '_SRT.rz')
                    else:
                        cmds.connectAttr(self.hand_control + '.masterRotation',
                                         finger_srt_sum + '.input1D[0]')
                        cmds.connectAttr(finger_srt_mult + '.outputX',
                                         finger_srt_sum + '.input1D[1]')
                        cmds.connectAttr(self.hand_control + '.' + finger_attr,
                                         finger_srt_sum + '.input1D[2]')
                        cmds.connectAttr(finger_srt_sum + '.output1D',
                                         finger_inverse_mdl + '.input1')
                        cmds.connectAttr(finger_inverse_mdl + '.output',
                                         segment + '_SRT.rz')

            offset_attr_factor = offset_attr_factor + 1
            reverse_attr_factor = reverse_attr_factor - 1
