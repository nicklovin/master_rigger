from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds


class NickRiggingUI(QtWidgets.QDialog):

    window_name = "Nick's Auto-Rigging GUI"

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle('Nick Auto-Rig Tool')

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(0)

        tab_layout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(tab_layout)

        # Create tab widget
        tab_widget = QtWidgets.QTabWidget()
        tab_layout.addWidget(tab_widget)

        # Create layouts for each tab (can be automated to be added)
        interface_tab_layout = QtWidgets.QVBoxLayout()
        other_tab_layout = QtWidgets.QVBoxLayout()

        # Create widgets for inside each tab, then set layouts from above
        interface_tab = QtWidgets.QWidget()
        tab_widget.addTab(interface_tab, 'interface')
        interface_tab.setFixedHeight(300)
        interface_tab.setFixedWidth(200)
        interface_tab.setLayout(interface_tab_layout)

        # Repeat
        other_tab = QtWidgets.QWidget()
        tab_widget.addTab(other_tab, 'other')
        other_tab.setFixedHeight(300)
        other_tab.setFixedWidth(200)
        other_tab.setLayout(other_tab_layout)

        # Creating widgets and items to go into each tab layout
        button1 = QtWidgets.QPushButton('button 1')
        button1.setFixedWidth(50)
        button1.setFixedHeight(50)
        interface_tab_layout.addWidget(button1)

        # Repeat
        button2 = QtWidgets.QPushButton('button 2')
        button2.setFixedWidth(100)
        button2.setFixedHeight(100)
        other_tab_layout.addWidget(button2)

        # parameter_widget = QtWidgets.QLabel('Test Layout')
        # parameter_widget.setLayout(interface_tab)


def show_ui():
    """
    Shows and returns handle to the UI
    Returns:
        QDialog
    """
    ui = NickRiggingUI()
    ui.show()
    return ui
