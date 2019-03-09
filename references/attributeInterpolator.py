from PySide2 import QtWidgets, QtGui, QtCore
import pymel.core as pm
import maya.cmds as cmds
from functools import partial
# Dockable options
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import widgets.button as button
reload(button)


class Interpolate(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Interpolate, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Interpolator')
        self.setFixedWidth(314)

        # Make adjustments to find the file location
        style_sheet_file = open('C:\Users\Nick Love\PycharmProjects\maya_tools\stylesheets\interpolate scheme.qss', 'r')
        self.setStyleSheet(style_sheet_file.read())

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFocusPolicy(QtCore.Qt.NoFocus)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout().addWidget(scroll_area)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('Interpolate')
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_widget.setLayout(main_layout)
        scroll_area.setWidget(self.main_widget)

        self.interp_layout = QtWidgets.QVBoxLayout()
        self.interp_layout.setContentsMargins(0, 0, 0, 0)
        self.interp_layout.setSpacing(0)
        self.interp_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.addLayout(self.interp_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        main_layout.addLayout(button_layout)

        add_button = button.DT_ButtonThin('New..')
        button_layout.addWidget(add_button)

        new_widget = InterpolateWidget()
        new_widget.hide_close_button()
        self.interp_layout.addWidget(new_widget)

        self._interp_widget = []
        self._interp_widget.append(new_widget)

        self._dock_name = self._dock_widget = None

        add_button.clicked.connect(self.add)

    def add(self):
        new_widget = InterpolateWidget()
        self.interp_layout.addWidget(new_widget)
        self._interp_widget.append(new_widget)
        new_widget.CLOSE.connect(partial(self.remove, new_widget))
        new_widget.setFixedHeight(0)
        new_widget._animate_expand(True)

    def remove(self, interp_widget, *args):  # *args takes unnecessary param
        interp_widget.DELETE.connect(partial(self._delete, interp_widget))
        self._interp_widget.remove(interp_widget)
        interp_widget._animate_expand(False)

    def _delete(self, interp_widget, *args):
        self.interp_layout.removeWidget(interp_widget)
        interp_widget._animation = None
        interp_widget.deleteLater()

    def connect_dock_widget(self, dock_name, dock_widget):  # Might be irrelevant
        self._dock_widget = dock_widget
        self._dock_name = dock_name

    def close_dock(self):
        if self._dock_widget:
            cmds.deleteUI(self._dock_name)
        else:
            QtWidgets.QDialog.close(self)
        self._dock_widget = self._dock_name = None


class InterpolateWidget(QtWidgets.QFrame):
    # signal variables
    CLOSE = QtCore.Signal(str)
    DELETE = QtCore.Signal(str)
    signal_close = 'CLOSE'
    signal_delete = 'DELETE'

    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        self.setFixedHeight(150)
        # self.setFixedWidth(320)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(3, 1, 3, 3)
        self.layout().setSpacing(0)
        self.setFixedHeight(150)

        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(QtWidgets.QVBoxLayout())
        main_widget.layout().setContentsMargins(2, 2, 2, 2)
        main_widget.layout().setSpacing(5)
        main_widget.setFixedHeight(140)
        main_widget.setFixedWidth(290)

        graphics_scene = QtWidgets.QGraphicsScene()
        graphics_view = QtWidgets.QGraphicsView()
        graphics_view.setScene(graphics_scene)
        graphics_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        graphics_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        graphics_view.setFocusPolicy(QtCore.Qt.NoFocus)
        graphics_view.setStyleSheet('QGraphicsView {border-style: none;}')
        graphics_view.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                    QtWidgets.QSizePolicy.Minimum)
        self.layout().addWidget(graphics_view)
        self.main_widget_proxy = graphics_scene.addWidget(main_widget)
        main_widget.setParent(graphics_view)

        title_layout = QtWidgets.QHBoxLayout()
        select_layout = QtWidgets.QHBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        slider_layout = QtWidgets.QHBoxLayout()
        check_layout = QtWidgets.QHBoxLayout()
        main_widget.layout().addLayout(title_layout)
        main_widget.layout().addLayout(select_layout)
        main_widget.layout().addLayout(button_layout)
        main_widget.layout().addLayout(slider_layout)
        main_widget.layout().addLayout(check_layout)

        title_line_edit = QtWidgets.QLineEdit('Untitled')
        title_line_edit.setFixedHeight(20)
        title_layout.addWidget(title_line_edit)

        self.close_button = QtWidgets.QPushButton('X')
        self.close_button.setObjectName('roundedButton')
        self.close_button.setFixedHeight(20)
        self.close_button.setFixedWidth(20)
        title_layout.addWidget(self.close_button)

        # store_items = QtWidgets.QPushButton('Store Items')
        store_items = button.DT_Button('Store Items')
        clear_items = button.DT_Button('Clear Items')

        select_layout.addSpacerItem(QtWidgets.QSpacerItem
                                    (5, 5, QtWidgets.QSizePolicy.Expanding))
        select_layout.addWidget(store_items)
        select_layout.addWidget(clear_items)
        select_layout.addSpacerItem(QtWidgets.QSpacerItem
                                    (5, 5, QtWidgets.QSizePolicy.Expanding))

        self.store_start_button = button.DT_ButtonThin('Store Start')
        self.reset_item_button = button.DT_ButtonThin('Reset')
        self.store_end_button = button.DT_ButtonThin('Store End')

        button_layout.addWidget(self.store_start_button)
        button_layout.addWidget(self.reset_item_button)
        button_layout.addWidget(self.store_end_button)

        self.start_label = QtWidgets.QLabel('Start')
        self.slider = QtWidgets.QSlider()
        self.slider.setRange(0, 49)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.end_label = QtWidgets.QLabel('End')

        slider_layout.addWidget(self.start_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.end_label)

        self.transforms_checkbox = QtWidgets.QCheckBox('Transform')
        self.attributes_checkbox = QtWidgets.QCheckBox('UD Attributes')
        self.transforms_checkbox.setCheckState(QtCore.Qt.Checked)

        check_layout.addWidget(self.transforms_checkbox)
        check_layout.addWidget(self.attributes_checkbox)

        self.items = {}
        self.slider_down = False
        self._animation = None

        self.close_button.clicked.connect(self.close_widget)

        store_items.clicked.connect(self.store_items)
        clear_items.clicked.connect(self.clear_items)

        self.store_start_button.clicked.connect(self.store_start)
        self.store_end_button.clicked.connect(self.store_end)
        self.reset_item_button.clicked.connect(self.reset_attributes)

        self.slider.valueChanged.connect(self.set_linear_interpolation)
        self.slider.sliderReleased.connect(self._end_slider_undo)

        self.enable_buttons(False)

    def _animate_expand(self, value):
        # opacity_anim = QtCore.QPropertyAnimation(self.main_widget_proxy,
        #                                          'opacity')
        # opacity_anim.setStartValue(not(value))
        # opacity_anim.setEndValue(value)
        # opacity_anim.setDuration(200)
        # opacity_anim_curve = QtCore.QEasingCurve()
        """if value:
            opacity_anim_curve.setType(QtCore.QEasingCurve.InQuad)
        else:
            opacity_anim_curve.setType(QtCore.QEasingCurve.OutQuad)
        opacity_anim.setEasingCurve(opacity_anim_curve)
        """
        size_anim = QtCore.QPropertyAnimation(self, 'geometry')

        geometry = self.geometry()
        width = geometry.width()
        x, y, _, _ = geometry.getCoords()  # _ variables accept info then dump

        size_start = QtCore.QRect(x, y, width, int(not(value) * 150))
        size_end = QtCore.QRect(x, y, width, int(value) * 150)

        size_anim.setStartValue(size_start)
        size_anim.setEndValue(size_end)
        size_anim.setDuration(300)

        size_anim_curve = QtCore.QEasingCurve()
        if value:
            size_anim_curve.setType(QtCore.QEasingCurve.InQuad)
        else:
            size_anim_curve.setType(QtCore.QEasingCurve.OutQuad)
        size_anim.setEasingCurve(size_anim_curve)

        self._animation = size_anim
        """
        if value:
            self.main_widget_proxy.setOpacity(0)
            self._animation.addAnimation(size_anim)
            self._animation.addAnimation(opacity_anim)
        else:
            self.main_widget_proxy.setOpacity(1)
            self._animation.addAnimation(opacity_anim)
            self._animation.addAnimation(size_anim)
        
        # self._animation.finished.connect(self._animation.clear)
        """
        size_anim.valueChanged.connect(self._force_resize)

        if not value:
            size_anim.finished.connect(self.delete_widget)
        size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _force_resize(self, new_height):
        self.setFixedHeight(new_height.height())

    def _start_slider_undo(self):
        pm.undoInfo(openChunk=True)

    def _end_slider_undo(self):
        pm.undoInfo(closeChunk=True)
        self.slider_down = False

    def store_items(self):
        selection = pm.ls(sl=True, fl=True)
        if not selection:
            return

        self.items = {}
        for node in selection:
            self.items[node.name()] = {'node': node,
                                       'start': {},
                                       'end': {},
                                       'cache': {}}

        self.enable_buttons(True)

    def clear_items(self):
        self.items = {}
        self.enable_buttons(False)

    def enable_buttons(self, value):
        self.store_start_button.setEnabled(value)
        self.reset_item_button.setEnabled(value)
        self.store_end_button.setEnabled(value)
        self.transforms_checkbox.setEnabled(value)
        self.attributes_checkbox.setEnabled(value)
        self.slider.setEnabled(value)
        self.start_label.setEnabled(value)
        self.end_label.setEnabled(value)

    def hide_close_button(self, value=True):
        self.close_button.setVisible(not(value))

    def store_start(self):
        if not self.items:
            return
        self._store('start', 0)
        self._cache()

    def store_end(self):
        if not self.items:
            return
        self._store('end', 50)
        self._cache()

    def _store(self, key, value):
        for item_dict in self.items.values():
            node = item_dict['node']
            attrs = self.get_attributes(node)
            data = item_dict[key]
            for attr in attrs:
                data[attr] = node.attr(attr).get()

            print item_dict

        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)

    def _cache(self):
        for item_dict in self.items.values():
            node = item_dict['node']
            start = item_dict['start']
            end = item_dict['end']
            if not start or not end:
                item_dict['cache'] = None
                continue

            attrs = list(set(start.keys()) and set(end.keys()))

            cache = item_dict['cache'] = {}
            for attr in attrs:
                start_attr = start[attr]
                end_attr = end[attr]

                if start_attr == end_attr:
                    cache[attr] = None
                else:
                    cache_values = cache[attr] = []
                    interval = float(end_attr - start_attr) / 49.0
                    for index in range(50):
                        cache_values.append((interval * index) + start_attr)

    def get_attributes(self, node):
        attrs = []
        if self.transforms_checkbox.isChecked():
            for transform in 'trs':
                for axis in 'xyz':
                    channel = '%s%s' % (transform, axis)
                    if node.attr(channel).isLocked():
                        continue
                    attrs.append(channel)

        if self.attributes_checkbox.isChecked():
            for attr in node.listAttr(userDefined=True):
                if attr.type() not in ('double', 'int'):
                    continue
                if attr.isLocked():
                    continue

                attrs.append(attr.name().split('.')[-1])

        return attrs

    def reset_attributes(self, *args):
        if not self.items:
            return

        for item_dict in self.items.values():
            node = item_dict['node']
            attrs = self.get_attributes(node)

            for attr in attrs:
                default_value = pm.attributeQuery(attr,
                                                  node=node,
                                                  listDefault=True)[0]
                node.attr(attr).set(default_value)

    def set_linear_interpolation(self, value):
        if not self.items:
            return

        if not self.slider_down:
            self._start_slider_undo()
            self.slider_down = True

        for item_dict in self.items.values():
            node = item_dict['node']
            start = item_dict['start']

            if not start or not item_dict['end']:
                continue

            cache = item_dict['cache']

            for attr in cache.keys():
                if cache[attr] is None:
                    continue
                pm.setAttr(node.attr(attr), cache[attr][value])

    def close_widget(self):
        self.CLOSE.emit(self.signal_close)

    def delete_widget(self):
        self.DELETE.emit(self.signal_delete)


dialog = None


def create_ui(docked=True):
    global dialog

    if dialog is None:
        dialog = Interpolate()
    if docked:
        dialog.show(dockable=True, floating=False, area='right')
    else:
        dialog.show()


def delete_ui():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None
