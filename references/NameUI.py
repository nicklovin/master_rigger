from PySide2 import QtWidgets, QtGui, QtCore


dialog = None


class NameUI(QtWidgets.QFrame):
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Name Tool')
        self.setFixedHeight(285)
        self.setFixedWidth(320)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignTop)


        # Rename Widget
        rename_widget = QtWidgets.QWidget()  # Widget holding upper name stuff
        rename_widget.setLayout(QtWidgets.QVBoxLayout())
        rename_widget.layout().setContentsMargins(0, 0, 0, 0)
        rename_widget.layout().setSpacing(2)
        rename_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                    QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(rename_widget)

        # Label Splitter
        rename_splitter = Splitter('Rename')  # Custom splitter widget
        rename_widget.layout().addWidget(rename_splitter)

        # Rename Input
        rename_text_layout = QtWidgets.QHBoxLayout()
        rename_text_layout.setContentsMargins(4, 0, 4, 0)
        rename_text_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_text_layout)

        rename_text_label = QtWidgets.QLabel('Rename: ')
        self.rename_line_edit = QtWidgets.QLineEdit()
        self.rename_line_edit.setPlaceholderText('C_objectName_##_CTRL')  # Grey text
        rename_text_layout.addWidget(rename_text_label)
        rename_text_layout.addWidget(self.rename_line_edit)

        # Regular Expression
        # () indicates excluding these symbols, [] indicates accepts these
        # Having a ^ between symbols indicates all symbols between are included
        reg_ex = QtCore.QRegExp('^(?!@$^_)[a-zA-Z_#]+')
        text_validator = QtGui.QRegExpValidator(reg_ex, self.rename_line_edit)
        self.rename_line_edit.setValidator(text_validator)

        rename_widget.layout().addLayout(SplitterLayout())

        # AlphaNumeric Options
        rename_alphanumberic_layout = QtWidgets.QHBoxLayout()
        rename_alphanumberic_layout.setContentsMargins(4, 0, 4, 0)
        rename_alphanumberic_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_alphanumberic_layout)

        rename_alphanumberic_label = QtWidgets.QLabel('Name List Method: ')
        self.rename_alpha_radio = QtWidgets.QRadioButton('Alpha')
        self.rename_number_radio = QtWidgets.QRadioButton('Numbers')
        self.rename_number_radio.setChecked(True)
        self.rename_alpha_radio.setFixedHeight(19)

        rename_alphanumberic_layout.addWidget(rename_alphanumberic_label)
        rename_alphanumberic_layout.addSpacerItem(
                QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        rename_alphanumberic_layout.addWidget(self.rename_alpha_radio)
        rename_alphanumberic_layout.addWidget(self.rename_number_radio)

        # Hidden Upper/Lower Case buttons
        rename_options_layout = QtWidgets.QHBoxLayout()
        rename_options_layout.setContentsMargins(4, 0, 4, 0)
        rename_options_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_options_layout)

        self.alpha_case_group = QtWidgets.QButtonGroup()
        self.lower_radio = QtWidgets.QRadioButton('Lowercase')
        self.upper_radio = QtWidgets.QRadioButton('Uppercase')
        self.alpha_case_group.addButton(self.lower_radio)
        self.alpha_case_group.addButton(self.upper_radio)
        self.lower_radio.setVisible(False)
        self.upper_radio.setVisible(False)
        self.lower_radio.setFixedHeight(19)
        self.upper_radio.setFixedHeight(19)
        self.upper_radio.setChecked(True)

        rename_options_layout.addWidget(self.lower_radio)
        rename_options_layout.addSpacerItem(
                QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        rename_options_layout.addWidget(self.upper_radio)

        # Starting Number
        rename_starting_number_layout = QtWidgets.QHBoxLayout()
        rename_starting_number_layout.setContentsMargins(4, 0, 4, 0)
        rename_starting_number_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_starting_number_layout)

        self.rename_start_label = QtWidgets.QLabel('Starting Number: ')
        self.rename_start_number = QtWidgets.QSpinBox()
        self.rename_start_number.setFixedWidth(50)
        self.rename_start_number.setMinimum(0)
        self.rename_start_number.setMaximum(999)
        self.rename_start_number.setValue(20)

        rename_starting_number_layout.addWidget(self.rename_start_label)
        rename_starting_number_layout.addWidget(self.rename_start_number)

        rename_widget.layout().addLayout(SplitterLayout())

        # Execute List Rename Button
        rename_button_layout = QtWidgets.QHBoxLayout()
        rename_button_layout.setContentsMargins(4, 0, 4, 0)
        rename_button_layout.setSpacing(0)
        rename_widget.layout().addLayout(rename_button_layout)

        self.rename_label = QtWidgets.QLabel('')
        rename_button = QtWidgets.QPushButton('Rename')
        rename_button.setFixedHeight(20)
        rename_button.setFixedWidth(55)

        rename_button_layout.addWidget(self.rename_label)
        rename_button_layout.addWidget(rename_button)


        # Replace Widget
        replace_widget = QtWidgets.QWidget()  # Widget holding lower name stuff
        replace_widget.setLayout(QtWidgets.QVBoxLayout())
        replace_widget.layout().setContentsMargins(0, 0, 0, 0)
        replace_widget.layout().setSpacing(2)
        replace_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(replace_widget)

        replace_splitter = Splitter('Find & Replace')  # Custom splitter widget
        replace_widget.layout().addWidget(replace_splitter)

        find_label = QtWidgets.QLabel('Find: ')
        self.find_line_edit = QtWidgets.QLineEdit()
        replace_label = QtWidgets.QLabel('Replace: ')
        self.replace_line_edit = QtWidgets.QLineEdit()

        find_label.setFixedWidth(55)
        replace_label.setFixedWidth(55)

        reg_ex = QtCore.QRegExp('[a-zA-Z_]+')
        text_validator = QtGui.QRegExpValidator(reg_ex, self.rename_line_edit)
        self.find_line_edit.setValidator(text_validator)
        self.replace_line_edit.setValidator(text_validator)

        find_layout = QtWidgets.QHBoxLayout()
        find_layout.setContentsMargins(4, 0, 4, 0)
        find_layout.setSpacing(2)
        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_line_edit)
        replace_widget.layout().addLayout(find_layout)

        replace_layout = QtWidgets.QHBoxLayout()
        replace_layout.setContentsMargins(4, 0, 4, 0)
        replace_layout.setSpacing(2)
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_line_edit)
        replace_widget.layout().addLayout(replace_layout)

        replace_widget.layout().addLayout(SplitterLayout())

        selection_layout = QtWidgets.QHBoxLayout()
        selection_layout.setContentsMargins(4, 0, 4, 0)
        selection_layout.setSpacing(2)
        replace_widget.layout().addLayout(selection_layout)

        selection_mode_label = QtWidgets.QLabel('Selection Mode: ')
        self.selected_radio_button = QtWidgets.QRadioButton('Selected')
        self.selected_radio_button.setFixedHeight(19)
        self.selected_radio_button.setChecked(True)
        self.hierarchy_radio_button = QtWidgets.QRadioButton('Hierarchy')
        self.hierarchy_radio_button.setFixedHeight(19)

        selection_layout.addWidget(selection_mode_label)
        spacer_item = QtWidgets.QSpacerItem(5, 5,
                                            QtWidgets.QSizePolicy.Expanding)
        selection_layout.addSpacerItem(spacer_item)
        selection_layout.addWidget(self.selected_radio_button)
        selection_layout.addWidget(self.hierarchy_radio_button)

        replace_widget.layout().addLayout(SplitterLayout())

        replace_button = QtWidgets.QPushButton('Replace')
        replace_button.setFixedHeight(20)
        replace_button.setFixedWidth(55)
        replace_button_layout = QtWidgets.QHBoxLayout()
        replace_button_layout.setContentsMargins(4, 0, 4, 0)
        replace_button_layout.setSpacing(0)
        replace_button_layout.setAlignment(QtCore.Qt.AlignRight)
        replace_button_layout.addWidget(replace_button)
        replace_widget.layout().addLayout(replace_button_layout)

        # State Change modifiers

        # Need to set the changed status of the alphanumeric radio buttons to
        # influence the _toggle_rename_vis() function
        self.rename_alpha_radio.clicked.connect(self._toggle_rename_vis)
        self.rename_number_radio.clicked.connect(self._toggle_rename_vis)

        self.lower_radio.clicked.connect(self._update_example)
        self.upper_radio.clicked.connect(self._update_example)
        self.rename_start_number.valueChanged.connect(self._update_example)

        self.rename_line_edit.textChanged.connect(self._update_example)

        rename_button.clicked.connect(self.list_rename)
        replace_button.clicked.connect(self.replace_text)

        self._update_example()

    def _toggle_rename_vis(self):
        visible = self.rename_alpha_radio.isChecked()
        self.lower_radio.setVisible(visible)
        self.upper_radio.setVisible(visible)
        self.rename_start_number.set

    def _get_rename_settings(self):
        text = str(self.rename_line_edit.text()).strip()

        naming_method = self.rename_number_radio.isChecked()

        starting_number = self.rename_start_number.value()

        upper = True
        if naming_method is False:
            upper = self.upper_radio.isChecked()

        return text, starting_number, naming_method, upper  # Use the parameters for the List rename tool

    def _update_example(self):
        example_text = ''

        text, starting_number, naming_method, upper = \
            self._get_rename_settings()

        if not text:  # text is a variable from above
            self.rename_label.setText('<font color=#646464>e.g.</font>')
            return

        example_text += text

        if not naming_method:
            if upper:
                if '#' in example_text:
                    padding = example_text.count('#')
                    if padding > 1:
                        full_pad = ''
                        for pad in range(padding):
                            full_pad += '#'
                        example_text = example_text.replace(full_pad, 'A')
                    else:
                        example_text = example_text.replace('#', 'A')
            else:
                if '#' in example_text:
                    padding = example_text.count('#')
                    if padding > 1:
                        full_pad = ''
                        for pad in range(padding):
                            full_pad += '#'
                        example_text = example_text.replace(full_pad, 'a')
                    else:
                        example_text = example_text.replace('#', 'a')
        else:
            if '#' in example_text:
                padding = example_text.count('#')
                if padding > 1:
                    full_pad = ''
                    for pad in range(padding):
                        full_pad += '#'
                    example_text = example_text.replace(
                            full_pad, str(starting_number).zfill(padding)
                    )
                else:
                    example_text = example_text.replace(
                            '#', str(starting_number).zfill(padding)
                    )

        self.rename_label.setText('<font color=#646464>e.g. %s</font>'
                                  % example_text)

    def list_rename(self):
        # Run the imported function from the renamer_library.py with the
        # parameters established above
        print 'RENAME'
        pass

    def replace_text(self):
        find_text = str(self.find_line_edit.text()).strip()
        replace_text = str(self.replace_line_edit.text()).strip()
        
        if self.selected_radio_button.isChecked():
            select_scope = 'selection'
        else:
            select_scope = 'hierarchy'

        print 'REPLACE'
        pass


class Splitter(QtWidgets.QWidget):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):
        QtWidgets.QWidget.__init__(self)

        self.setMinimumHeight(2)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignVCenter)

        first_line = QtWidgets.QFrame()
        first_line.setFrameStyle(QtWidgets.QFrame.HLine)
        self.layout().addWidget(first_line)

        main_color = 'rgba(%s, %s, %s, 255)' % color
        shadow_color = 'rgba(45, 45, 45, 255)'

        bottom_border = ''
        if shadow:
            bottom_border = 'border-bottom: 1px solid %s;' % shadow_color

        style_sheet = "border:0px solid rgba(0, 0, 0, 0);" \
                      "background-color: %s;" \
                      "max-height: 1px;" \
                      "%s" % (main_color, bottom_border)
        first_line.setStyleSheet(style_sheet)

        if text is None:
            return

        first_line.setMaximumWidth(5)

        font = QtGui.QFont()
        font.setBold(True)

        text_width = QtGui.QFontMetrics(font)
        width = text_width.width(text) + 6

        label = QtWidgets.QLabel()
        label.setText(text)
        label.setFont(font)
        label.setMaximumWidth(width)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.layout().addWidget(label)

        second_line = QtWidgets.QFrame()
        second_line.setFrameStyle(QtWidgets.QFrame.HLine)
        second_line.setStyleSheet(style_sheet)
        self.layout().addWidget(second_line)


class SplitterLayout(QtWidgets.QHBoxLayout):
    def __init__(self):
        QtWidgets.QHBoxLayout.__init__(self)
        self.setContentsMargins(40, 2, 40, 2)

        splitter = Splitter(shadow=False, color=(60, 60, 60))
        splitter.setFixedHeight(1)

        self.addWidget(splitter)


def create_name_ui():
    global dialog
    if dialog is None:
        dialog = NameUI()
    dialog.show()


def delete_name_ui():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None
