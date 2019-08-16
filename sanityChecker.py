# Sanity Checker pre-rig publish
import maya.mel as mel
import maya.cmds as cmds


def sanityCheck(deleteUnusedNodes):
	# lock/hide all non-animator friendly objects
	objectsToHide = []
	objectsToLock = []
	nodesToDelete = []

	# locators
	locators = [cmds.listRelatives(loc, parent=True)[0] for loc in cmds.ls(type='locator')]
	objectsToHide.extend(locators)
	objectsToLock.extend(locators)

	# TODO: rip group names from offset group list in widget
	influenceNodes = [
		'SRT', 'SDK', 'OFS', 'ZERO', 'GRP', 'CNS', 'INFLU', 'SPACE', 'DUMMY', 'NULL', 'EXPR']

	allNodes = cmds.ls()
	transforms = [node for node in allNodes if node.endswith(influenceNodes)]
	controls = [node for node in allNodes if node.endswith('CTL')]
	objectsToLock.extend(transforms)

	keyframes = cmds.ls(type=('animCurveTL', 'animCurveTU', 'animCurveTA', 'animCurveTT'))
	if keyframes:
		nodesToDelete.extend(keyframes)

	setDrivenKeys = cmds.ls(type=('animCurveUL', 'animCurveUU', 'animCurveUA', 'animCurveUT'))
	if setDrivenKeys:
		objectsToHide.extend(setDrivenKeys)

	# Check for repeat names/longname issues
	nodesToRename = []
	# TODO: make cleaner?
	for node in allNodes:
		if len(cmds.ls(node.split('|')[-1])) > 1:
			nodesToRename.append(node)

	nonZeroTransforms = []
	for node in allNodes:
		transforms = [
			'{}.{}'.format(node, attr) for attr in ['tx', 'ty', 'tx', 'rx', 'ry', 'rz']
			if cmds.getAttr('{}.{}'.format(node, attr)) != 0]
		if len(transforms):
			nonZeroTransforms.extend(transforms)

	# Make a prompt for this option
	if deleteUnusedNodes:
		mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
