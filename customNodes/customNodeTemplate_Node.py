# import the api
from maya.api import OpenMaya as om


# Let maya know we're using it by declaring this function
def maya_useNewAPI():
    pass


# We'll be making our node by deriving from MPxNode, a base class for all nodes
class FloatToThreeNode(om.MPxNode):
    # Define the name of the node
    kNodeName = 'floatTo3'

    # Must be a random hex number to register with Maya
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

    # def __init__(self):
    #     om.MPxNode.__init__(self)

    # Similar to the other plugins we need a creator
    @classmethod
    def creator(cls):
        return cls()

    # We also need an initialize method that will set up the plugs and attributes on our nodes
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


def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)

    try:
        pluginFn.registerNode(
            FloatToThreeNode.kNodeName,  # The name of the node
            FloatToThreeNode.kNodeID,  # The unique ID for this node
            FloatToThreeNode.creator,  # The function to create this node
            FloatToThreeNode.initialize,  # The function to initalize the node
        )
    except:
        om.MGlobal.displayError('Failed to register node %s' % FloatToThreeNode.kNodeName)
        raise


def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)

    try:
        pluginFn.deregisterNode(FloatToThreeNode.kNodeID)
    except:
        om.MGlobal.displayError('Failed to unregister node %s' % FloatToThreeNode.kNodeName)
        raise


"""
To load
from Nodes import FloatToThreeNode
import maya.cmds as mc

mc.file(new=True, force=True)

try:
    # Force is important
    mc.unloadPlugin('FloatToThreeNode', force=True)
finally:
    mc.loadPlugin(FloatToThreeNode.__file__)
"""
