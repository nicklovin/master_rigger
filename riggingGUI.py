from functools import partial
from Qt import QtWidgets, QtCore, QtGui
import maya.cmds as cmds


class NickRiggingUI(QtWidgets.QDialog):

    window_name = "Nick's Auto-Rigging GUI"

    def __init__(self):
        super(NickRiggingUI, self).__init__()

        self.setWindowTitle('Playblast Shapes UI')

        self.build_ui()

    def build_ui(self):
        # Master Layout
        layout = QtWidgets.QGridLayout(self)

        # parameter widgets
        self.frame_interval_text = QtWidgets.QLabel('Pose Interval')
        layout.addWidget(self.frame_interval_text, 0, 0, 1, 1)
        self.frame_interval_field = QtWidgets.QLineEdit('24')
        layout.addWidget(self.frame_interval_field, 0, 1, 1, 2)

        self.frame_hold_text = QtWidgets.QLabel('Hold Pose Interval')
        layout.addWidget(self.frame_hold_text, 1, 0, 1, 1)
        self.frame_hold_field = QtWidgets.QLineEdit('12')
        layout.addWidget(self.frame_hold_field, 1, 1, 1, 2)

        self.prefix_filter_text = QtWidgets.QLabel('Prefix Filters')
        layout.addWidget(self.prefix_filter_text, 2, 0, 1, 1)
        self.name_filter_field = QtWidgets.QLineEdit('lcr')
        layout.addWidget(self.name_filter_field, 2, 1, 1, 2)

        run_command_button = QtWidgets.QPushButton('Playblast Face Shapes')
        run_command_button.clicked.connect(self.run_playblast)
        layout.addWidget(run_command_button, 3, 0, 1, 3)

    def run_playblast(self):
        # Check if command should run based on input values
        input_status = self.check_input()
        if not input_status:
            return

        interval_input = int(self.frame_interval_field.text())
        hold_input = int(self.frame_hold_field.text())
        filter_input = self.name_filter_field.text()

        # Running the script

    def check_input(self):
        # checking value type of interval field
        try:
            interval_input = int(self.frame_interval_field.text())
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error',
                                        'Pose Interval: '
                                        'Input can only be an integer')
            return False

        try:
            hold_input = int(self.frame_hold_field.text())
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error',
                                        'Hold Pose Interval: '
                                        'Input can only be an integer')
            return False

        else:
            return True


def show_ui():
    """
    Shows and returns handle to the UI
    Returns:
        QDialog
    """
    ui = NickRiggingUI()
    ui.show()
    return ui
