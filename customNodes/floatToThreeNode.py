import traceback

from maya.api import OpenMaya as om


# Let maya know we're using it by declaring this function
def maya_useNewAPI():
    pass


class FloatToThreeNode(om.MPxNode):

    kNodeName = 'floatTo3'

    kNodeID = om.MTypeId(0x11111)

    # Input
    kInput = None
    kInputA_AttrName = 'in'
    kInputA_AttrLongName = 'input'

    # Output
    kOutput = None
    kOutputXAttr = None
    kOutputYAttr = None
    kOutputZAttr = None
    kOutput_AttrName = 'out'
    kOutput_AttrLongName = 'output'

    @classmethod
    def creator(cls):
        return cls()

    @classmethod
    def initialize(cls):
        nAttr = om.MFnNumericAttribute()

        # Input Attr
        cls.kInput = nAttr.create(
            cls.kInputA_AttrLongName,
            cls.kInputA_AttrName,
            om.MFnNumericData.kDouble)
        nAttr.keyable = True

        # Output Attrs
        cls.kOutputXAttr = nAttr.create(
            cls.kOutput_AttrLongName + 'X',
            cls.kOutput_AttrName + 'X',
            om.MFnNumericData.kDouble)
        nAttr.storable = True
        nAttr.writable = True
        cls.kOutputYAttr = nAttr.create(
            cls.kOutput_AttrLongName + 'Y',
            cls.kOutput_AttrName + 'Y',
            om.MFnNumericData.kDouble)
        nAttr.storable = True
        nAttr.writable = True
        cls.kOutputZAttr = nAttr.create(
            cls.kOutput_AttrLongName + 'Z',
            cls.kOutput_AttrName + 'Z',
            om.MFnNumericData.kDouble)
        nAttr.storable = True
        nAttr.writable = True
        cls.kOutput = nAttr.create(
            cls.kOutput_AttrLongName,
            cls.kOutput_AttrName,
            cls.kOutputXAttr,
            cls.kOutputYAttr,
            cls.kOutputZAttr)
        nAttr.storable = False
        nAttr.writable = True

        # Apply Attrs to node
        cls.addAttribute(cls.kInput)
        cls.addAttribute(cls.kOutput)

        # Assign inputs affecting outputs
        cls.attributeAffects(cls.kInput, cls.kOutput)

    def compute(self, plug, data):
        if plug != FloatToThreeNode.kOutput:
            return

        # The inputValue gives us back an MDataHandle
        inHandle = data.inputValue(FloatToThreeNode.kInput)
        inDouble = inHandle.asDouble()

        # Then we can set this value on our node
        outHandle = data.outputValue(FloatToThreeNode.kOutput)
        outHandle.set3Double(inDouble, inDouble, inDouble)

        data.setClean(plug)


class AngleToThreeNode(om.MPxNode):

    kNodeName = 'angleTo3'

    kNodeID = om.MTypeId(0x10000)

    # Input
    kInput = None
    kInputA_AttrName = 'in'
    kInputA_AttrLongName = 'input'

    # Output
    kOutput = None
    kOutputXAttr = None
    kOutputYAttr = None
    kOutputZAttr = None
    kOutput_AttrName = 'out'
    kOutput_AttrLongName = 'output'

    @classmethod
    def creator(cls):
        return cls()

    @classmethod
    def initialize(cls):
        nAttr = om.MFnNumericAttribute()
        uAttr = om.MFnUnitAttribute()

        # Input Attr
        cls.kInput = uAttr.create(
            cls.kInputA_AttrLongName,
            cls.kInputA_AttrName,
            om.MFnUnitAttribute.kAngle)
        uAttr.keyable = True

        # Output Attrs
        cls.kOutputXAttr = uAttr.create(
            cls.kOutput_AttrLongName + 'X',
            cls.kOutput_AttrName + 'X',
            om.MFnUnitAttribute.kAngle)
        uAttr.storable = True
        uAttr.writable = True
        cls.kOutputYAttr = uAttr.create(
            cls.kOutput_AttrLongName + 'Y',
            cls.kOutput_AttrName + 'Y',
            om.MFnUnitAttribute.kAngle)
        uAttr.storable = True
        uAttr.writable = True
        cls.kOutputZAttr = uAttr.create(
            cls.kOutput_AttrLongName + 'Z',
            cls.kOutput_AttrName + 'Z',
            om.MFnUnitAttribute.kAngle)
        uAttr.storable = True
        uAttr.writable = True
        cls.kOutput = nAttr.create(
            cls.kOutput_AttrLongName,
            cls.kOutput_AttrName,
            cls.kOutputXAttr,
            cls.kOutputYAttr,
            cls.kOutputZAttr)
        uAttr.storable = False
        uAttr.writable = True

        # Apply Attrs to node
        cls.addAttribute(cls.kInput)
        cls.addAttribute(cls.kOutput)

        # Assign inputs affecting outputs
        cls.attributeAffects(cls.kInput, cls.kOutput)

    def compute(self, plug, data):
        if plug != AngleToThreeNode.kOutput:
            return

        # The inputValue gives us back an MDataHandle
        inHandle = data.inputValue(AngleToThreeNode.kInput)
        inDouble = inHandle.asDouble()

        # Then we can set this value on our node
        outHandle = data.outputValue(AngleToThreeNode.kOutput)
        outHandle.set3Double(inDouble, inDouble, inDouble)

        data.setClean(plug)


def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)

    try:
        pluginFn.registerNode(
            FloatToThreeNode.kNodeName,
            FloatToThreeNode.kNodeID,
            FloatToThreeNode.creator,
            FloatToThreeNode.initialize,
        )
    except Exception as err:
        om.MGlobal.displayError('Failed to register node %s' % FloatToThreeNode.kNodeName)
        traceback.print_exc(err)
        raise

    try:
        pluginFn.registerNode(
            AngleToThreeNode.kNodeName,
            AngleToThreeNode.kNodeID,
            AngleToThreeNode.creator,
            AngleToThreeNode.initialize,
        )
    except Exception as err:
        om.MGlobal.displayError('Failed to register node %s' % AngleToThreeNode.kNodeName)
        traceback.print_exc(err)
        raise


def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)

    try:
        pluginFn.deregisterNode(FloatToThreeNode.kNodeID)
    except:
        om.MGlobal.displayError('Failed to unregister node %s' % FloatToThreeNode.kNodeName)
        raise
