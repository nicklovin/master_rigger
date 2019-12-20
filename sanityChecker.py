# Sanity Checker pre-rig publish
import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm

from master_rigger import attributeManipulation as atManip


influenceNodes = (
	'SRT',
	'SDK',
	'OFS',
	'ZERO',
	'GRP',
	'CNS',
	'INFLU',
	'SPACE',
	'DUMMY',
	'NULL',
	'EXPR',
	'PIV',
	'PIVOT',
	'LOC'  # Should be depricated, but still exists in some rigs
)


def publishMode(deleteUnusedNodes=False):
	selectedRig = pm.ls(selection=True)[0]
	# lock/hide all non-animator friendly nodes
	nodesToHide = []
	nodesToLock = []
	nodesToDelete = []

	# locators
	locators = pm.ls(type='locator')
	nodesToHide.extend(locators)

	# TODO: rip group names from offset group list in widget

	# allNodes = pm.ls()
	hierarchyNodes = pm.listRelatives(selectedRig, allDescendents=True)
	transforms = [
		node for node in hierarchyNodes
		if node.name().endswith(influenceNodes) and node.type() == 'transform'
	]
	controls = [node for node in hierarchyNodes if node.name().endswith('CTL')]
	nodesToLock.extend(transforms)

	keyframes = cmds.ls(type=('animCurveTL', 'animCurveTU', 'animCurveTA', 'animCurveTT'))
	if keyframes:
		nodesToDelete.extend(keyframes)

	# Known hierarchy groups to hide
	nodesToHide.extend([
		pm.ls(node)[0]
		for node in ['JNT_GRP', 'IK_GRP', 'MISC_NODES_GRP', 'SCRIPT_NODES_GRP', 'DEFORMER_GRP']])

	# setDrivenKeys = cmds.ls(type=('animCurveUL', 'animCurveUU', 'animCurveUA', 'animCurveUT'))

	# Check for repeat names/longname issues
	# nodesToRename = []
	# TODO: make cleaner?
	# for node in hierarchyNodes:
	# 	if len(cmds.ls(node.split('|')[-1])) > 1:
	# 		nodesToRename.append(node)

	for node in controls:
		transforms = any([
			cmds.getAttr('{}.{}'.format(node, attr)) != 0
			for attr in ['tx', 'ty', 'tx', 'rx', 'ry', 'rz']])
		if transforms:
			print transforms
			atManip.reset_transforms(node)

	pm.delete(nodesToDelete)
	for node in nodesToHide:
		node.visibility.set(0)

	atManip.lock_hide(1, 1, 1, 1, 1, 1, 1, 1, 1, 0, objects=nodesToLock, hide=False)

	# Make a prompt for this option
	if deleteUnusedNodes:
		mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')

	print 'publish mode initiated'


def editMode():
	selectedRig = pm.ls(selection=True)[0]
	nodesToShow = []
	nodesToUnlock = []

	# locators
	locators = pm.ls(type='locator')
	nodesToShow.extend(locators)

	for node in nodesToShow:
		node.visibility.set(1)

	hierarchyNodes = pm.listRelatives(selectedRig, allDescendents=True)
	transforms = [
		node for node in hierarchyNodes
		if node.name().endswith(influenceNodes) and node.type() == 'transform'
	]
	nodesToUnlock.extend(transforms)

	atManip.lock_hide(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, objects=nodesToUnlock, hide=False)
	print 'edit mode initiated'
