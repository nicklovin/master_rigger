import maya.cmds as cmds
from string import ascii_uppercase
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import Splitter

LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}


def get_short_name(longname):
    """
    Returns the shortname of an input object.
    """
    short_name = longname.rsplit('|', 1)[-1]
    return short_name


def get_long_name(name):
    """
    Returns the longname of an object.
    """
    long_name = cmds.ls(name, long=True)[0]
    return long_name


def list_renamer(new_name, numeric_index=True, start_number=1,
                 upper_case=True, end_name=False, selection=True,
                 list_input=[]):
    """
    Renamer tool for renaming lists of objects.  Default works based off
    selection, but can take a list parameter when function is passed with larger
    tools and functions.

    Args:
        new_name (str): Name to assign to object list. Must include at least
            one '#'.
        numeric_index (bool): Assign numeric values to the padding of renamed
            objects in the list.  If false, uses alphanumeric.
        start_number (int): Assign starting index for the numeric renaming.  In
            alphanumeric, it will apply to the corresponding letter position.
            (ex. 2 = 'B')
        upper_case (bool): Assign  alphabet identifier as uppercase or lowercase.
        end_name (bool): Assign if the last object in the list should have the
            numeric value replaced with 'END'.
        selection (bool): Assign if the input should query the selection or an
            input list.  Default is True.
        list_input (list[str]): Assign the function to perform based on a list
            input not limited to selection.  Only active when selection argument
            is False.

    Returns:
        (list): List of all the newly named nodes.

    """
    if selection:
        name_list = cmds.ls(selection=True, long=True)
    else:
        name_list = list_input
    index_start = max(0, start_number)

    if '#' not in new_name:
        cmds.warning('Could not find any "#" in name.')
        return

    pad_replace = ''
    number_padding = new_name.count('#')
    for i in range(number_padding):
        pad_replace = pad_replace + '#'

    new_name_list = []
    # Numeric renaming
    if numeric_index:
        index = index_start

        for i in name_list:
            padded_index = str(index).zfill(number_padding)
            cmds.rename(i, new_name.replace(pad_replace, padded_index))
            new_name_list.append(new_name.replace(pad_replace, padded_index))
            index = index + 1

    # Alphanumeric renaming
    else:
        # If index is not 0, the index will be changed to start letters at
        # appropriate alphanumeric count
        if index_start > 0:
            index = index_start
        else:
            index = 1

        if name_list > 26:
            pass

            # index[27] == 'aa'
        letter_index = None
        overlap_count = 0
        for i in name_list:
            # Remainder division (not substitution)
            continuous_index = index % 27

            if continuous_index < index:
                overlap_count = overlap_count + 1
                letter_index = LETTERS_INDEX[overlap_count]
                index = 1
            if letter_index:
                if upper_case:
                    padded_index = letter_index + LETTERS_INDEX[index]
                else:
                    padded_index = letter_index.lower() \
                                   + str(LETTERS_INDEX[index]).lower()

            else:
                if upper_case:
                    padded_index = LETTERS_INDEX[index]
                else:
                    padded_index = str(LETTERS_INDEX[index]).lower()

            cmds.rename(i, new_name.replace(pad_replace, padded_index))
            new_name_list.append(new_name.replace(pad_replace, padded_index))
            index = index + 1

    # After indexes are all named, check if last object should be an 'end'
    if end_name:
        new_name_list[-1] = cmds.rename(new_name_list[-1],
                                        new_name.replace(pad_replace, 'END'))

    return new_name_list


def set_prefix(input_prefix, add=True, replace=False, remove=False,
               list_input=[]):
    """
    Prefix setting tool.  Allows for a prefix to be added, replaced, or removed
    based on user input.  Users must declare one of the Procedure Type Arguments
    to be True, and leave the other two as False for the function to run.
    Default works based off selection, but can take a list parameter when
    function is passed with larger tools and functions.

    Args:
        input_prefix (str): Assign the string value to add as a prefix.
        Procedure Type Arguments:
            add (bool): Assign the function to add a new prefix
            replace (bool): Assign the function to replace an existing prefix
            remove (bool): Assign the function to remove an existing prefix.
        list_input (list[str]): Allows for a provided list to be performed on.
            Only works if selection flag is False.

    """
    if (add and replace) or (add and remove) or (replace and remove):
        cmds.error('Can only set one type flag at a time!  Use only one of'
                   ' the following: add, replace, remove.')

    if not add and not replace and not remove:
        cmds.error('No argument specified for the function to perform!  Set a '
                   'value of True to one of the following: add, replace, '
                   'remove.')

    if not list_input:
        name_list = cmds.ls(selection=True, long=True)
    else:
        name_list = list_input

    name_return_list = []

    if add:
        for i in name_list:
            short_i = get_short_name(i)
            if i[0] == '_':
                new_i = cmds.rename(i, short_i[1:])
                new_name = cmds.rename(new_i, '%s_%s' % (input_prefix, new_i))
            else:
                new_name = cmds.rename(i, '%s_%s' % (input_prefix, short_i))
            name_return_list.append(new_name)
        return name_return_list

    if replace:
        kill_length_list = []
        for obj in name_list:
            kill_length = obj.find('_')
            kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            new_name = cmds.rename(
                i, i.replace(i[0:kill_length_list[number]], input_prefix))
            number = number + 1
            name_return_list.append(new_name)
        return name_return_list

    if remove:
        kill_length_list = []
        for obj in name_list:
            if '_' in obj:
                kill_length = obj.find('_')
                kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            if i[0] == '_':
                new_name = cmds.rename(i, i[1:])
            elif i[0] is int:
                cmds.warning('Removing the prefix causes object to begin with '
                             'illegal characters (integer). Object skipped for '
                             'procedure.')
            else:
                new_name = cmds.rename(
                        i, i[0:(kill_length_list[number] + 1)])
            number = number + 1
            name_return_list.append(new_name)
        return name_return_list


def set_suffix(input_suffix, add=True, replace=False, remove=False,
               list_input=[]):
    """
    Prefix setting tool.  Allows for a suffix to be added, replaced, or removed
    based on user input.  Users must declare one of the Procedure Type Arguments
    to be True, and leave the other two as False for the function to run.
    Default works based off selection, but can take a list parameter when
    function is passed with larger tools and functions.

    Args:
        input_suffix (str): Assign the string value to add as a suffix.
        Procedure Type Arguments:
            add (bool): Assign the function to add a new suffix
            replace (bool): Assign the function to replace an existing suffix
            remove (bool): Assign the function to remove an existing suffix.
        list_input (list[str]): Allows for a provided list to be performed on.
            Only works if selection flag is False.

    """
    if (add and replace) or (add and remove) or (replace and remove):
        cmds.error('Can only set one type flag at a time!  Use only one of'
                   ' the following: add, replace, remove.')

    if not add and not replace and not remove:
        cmds.error('No argument specified for the function to perform!  Set a '
                   'value of True to one of the following: add, replace, '
                   'remove.')

    if not list_input:
        name_list = cmds.ls(selection=True, long=True)
    else:
        name_list = list_input

    name_return_list = []

    if add:
        for i in name_list:
            short_i = get_short_name(i)
            if i[-1] == '_':
                new_name = cmds.rename(i, '%s%s' % (short_i, input_suffix))
            else:
                new_name = cmds.rename(i, '%s_%s' % (short_i, input_suffix))
            # Test string to diagnose why function is not iterating properly:
            print '{} -> {}'.format(short_i, new_name)
            name_return_list.append(new_name)

    if replace:
        kill_length_list = []
        for obj in name_list:
            if '_' in obj:
                kill_length = obj.rfind('_')
                kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            if i[-1] == '_':
                new_name = cmds.rename(i, '%s%s' % (i, input_suffix))
            else:
                new_name = cmds.rename(i,
                                       '%s_%s' % (i[:kill_length_list[number]],
                                                  input_suffix))
                print i[kill_length_list[number]:]
            name_return_list.append(new_name)
            number = number + 1

    if remove:
        kill_length_list = []
        for obj in name_list:
            kill_length = obj.rfind('_')
            kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            if i[-1] == '_':
                cmds.rename(i, i[1:-1])
            else:
                new_name = \
                    cmds.rename(i, i[kill_length_list[number]:])
                name_return_list.append(new_name)
            number = number + 1

    return name_return_list


def search_replace_name(search_input, replace_output, hierarchy=False,
                        input_object=[]):
    """
    Python equivalent of the mel searchReplaceNames procedure.  Created to work
    with GUIs and python-written scripts.

    Args:
        search_input (str): String to search for that will be replaced.
        replace_output (str): String used to replace the input string.
        hierarchy (bool): Declare the range/scope of the procedure to use all
            objects in hierarchy instead of just selection.
        input_object (list[str]): Allows funciton to work based on a provided
            list.  If nothing given, selection is assumed.

    """
    name_return_list = []

    if not hierarchy:
        if input_object:
            selection = input_object
        else:
            selection = cmds.ls(selection=True, long=True)
        for obj in selection:
            if search_input in obj:
                new_name = cmds.rename(obj, get_short_name(obj).replace
                                       (search_input, replace_output))
                name_return_list.append(new_name)

    else:
        if input_object:
            hierarchy = cmds.listRelatives(input_object) \
                        + cmds.ls(selection=True, long=True)
        else:
            hierarchy = cmds.listRelatives(cmds.ls(selection=True, long=True)[0],
                                           allDescendents=True) \
                        + cmds.ls(selection=True, long=True)
        for obj in hierarchy:
            if search_input in obj:
                new_name = cmds.rename(obj, obj.replace
                                       (search_input, replace_output))
                name_return_list.append(new_name)

    return name_return_list


def clear_end_digits(input_object=[]):
    name_return_list = []

    if not input_object:
        input_object = cmds.ls(selection=True, long=True)

    for obj in input_object:
        try:
            int(obj[-1])
        except ValueError:
            continue

        if cmds.objExists(obj[0:-1]):
            cmds.warning('While removing end digits, another object with name '
                         '"{}" was found.  Function may have failed to remove '
                         'end digits properly.'.format(obj[0:-1]))

        new_name = cmds.rename(obj, obj[0:-1])
        name_return_list.append(new_name)

    return name_return_list


class NamingWidget(QtWidgets.QFrame):
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Name Tool')
        self.setMinimumHeight(285)
        self.setMinimumWidth(320)

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
        rename_splitter = Splitter.Splitter('Rename')  # Custom splitter widget
        rename_widget.layout().addWidget(rename_splitter)

        # Rename Input
        rename_text_layout = QtWidgets.QHBoxLayout()
        rename_text_layout.setContentsMargins(4, 0, 4, 0)
        rename_text_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_text_layout)

        rename_text_label = QtWidgets.QLabel('Rename: ')
        self.rename_line_edit = QtWidgets.QLineEdit()
        self.rename_line_edit.setPlaceholderText(
            'C_objectName_##_CTRL')  # Grey text
        rename_text_layout.addWidget(rename_text_label)
        rename_text_layout.addWidget(self.rename_line_edit)

        # Regular Expression
        # () indicates excluding these symbols, [] indicates accepts these
        # Having a ^ between symbols indicates all symbols between are included
        reg_ex = QtCore.QRegExp('^(?!@$^_)[0-9a-zA-Z_#]+')
        text_validator = QtGui.QRegExpValidator(reg_ex, self.rename_line_edit)
        self.rename_line_edit.setValidator(text_validator)

        rename_widget.layout().addLayout(Splitter.SplitterLayout())

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

        self.list_end_condition_label = QtWidgets.QLabel('End with "END":')
        self.list_end_condition_checkbox = QtWidgets.QCheckBox()

        rename_starting_number_layout.addWidget(self.rename_start_label)
        rename_starting_number_layout.addWidget(self.rename_start_number)
        rename_starting_number_layout.addSpacerItem(
            QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding)
        )
        rename_starting_number_layout.addWidget(self.list_end_condition_label)
        rename_starting_number_layout.addWidget(
            self.list_end_condition_checkbox)

        rename_widget.layout().addLayout(Splitter.SplitterLayout())

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

        replace_splitter = Splitter.Splitter('Find & Replace')
        replace_widget.layout().addWidget(replace_splitter)

        find_label = QtWidgets.QLabel('Find: ')
        self.find_line_edit = QtWidgets.QLineEdit()
        replace_label = QtWidgets.QLabel('Replace: ')
        self.replace_line_edit = QtWidgets.QLineEdit()

        find_label.setFixedWidth(55)
        replace_label.setFixedWidth(55)

        reg_ex = QtCore.QRegExp('[0-9a-zA-Z_]+')
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

        replace_widget.layout().addLayout(Splitter.SplitterLayout())

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

        replace_widget.layout().addLayout(Splitter.SplitterLayout())

        replace_button = QtWidgets.QPushButton('Replace')
        replace_button.setFixedHeight(20)
        replace_button.setFixedWidth(55)
        replace_button_layout = QtWidgets.QHBoxLayout()
        replace_button_layout.setContentsMargins(4, 0, 4, 0)
        replace_button_layout.setSpacing(0)
        replace_button_layout.setAlignment(QtCore.Qt.AlignRight)
        replace_button_layout.addWidget(replace_button)
        replace_widget.layout().addLayout(replace_button_layout)

        # Prefix and Suffix
        additions_widget = QtWidgets.QWidget()
        additions_widget.setLayout(QtWidgets.QVBoxLayout())
        additions_widget.layout().setContentsMargins(0, 0, 0, 0)
        additions_widget.layout().setSpacing(2)
        additions_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                       QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(additions_widget)

        # Label Splitter
        additions_splitter = Splitter.Splitter('Prefix & Suffix')
        additions_widget.layout().addWidget(additions_splitter)

        prefix_layout = QtWidgets.QHBoxLayout()
        prefix_layout.setContentsMargins(4, 0, 4, 0)
        prefix_layout.setSpacing(2)
        additions_widget.layout().addLayout(prefix_layout)

        suffix_layout = QtWidgets.QHBoxLayout()
        suffix_layout.setContentsMargins(4, 0, 4, 0)
        suffix_layout.setSpacing(2)
        additions_widget.layout().addLayout(suffix_layout)

        prefix_label = QtWidgets.QLabel('Prefix:')
        self.prefix_line_edit = QtWidgets.QLineEdit()
        self.prefix_add_button = QtWidgets.QPushButton('+')
        self.prefix_remove_button = QtWidgets.QPushButton('-')
        self.prefix_replace_button = QtWidgets.QPushButton('><')  # Change later

        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_line_edit)
        prefix_layout.addWidget(self.prefix_add_button)
        prefix_layout.addWidget(self.prefix_remove_button)
        prefix_layout.addWidget(self.prefix_replace_button)

        suffix_label = QtWidgets.QLabel('Suffix:')
        self.suffix_line_edit = QtWidgets.QLineEdit()
        self.suffix_add_button = QtWidgets.QPushButton('+')
        self.suffix_remove_button = QtWidgets.QPushButton('-')
        self.suffix_replace_button = QtWidgets.QPushButton('><')  # Change later

        suffix_layout.addWidget(suffix_label)
        suffix_layout.addWidget(self.suffix_line_edit)
        suffix_layout.addWidget(self.suffix_add_button)
        suffix_layout.addWidget(self.suffix_remove_button)
        suffix_layout.addWidget(self.suffix_replace_button)

        prefix_label.setFixedWidth(55)
        suffix_label.setFixedWidth(55)

        self.prefix_add_button.setFixedWidth(25)
        self.prefix_remove_button.setFixedWidth(25)
        self.prefix_replace_button.setFixedWidth(25)
        self.suffix_add_button.setFixedWidth(25)
        self.suffix_remove_button.setFixedWidth(25)
        self.suffix_replace_button.setFixedWidth(25)

        additions_widget.layout().addLayout(Splitter.SplitterLayout())

        # Name Cleanup
        cleanup_widget = QtWidgets.QWidget()
        cleanup_widget.setLayout(QtWidgets.QVBoxLayout())
        cleanup_widget.layout().setContentsMargins(0, 0, 0, 0)
        cleanup_widget.layout().setSpacing(2)
        cleanup_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Fixed)
        self.layout().addWidget(cleanup_widget)

        # Label Splitter
        cleanup_splitter = Splitter.Splitter('Cleanup')
        cleanup_widget.layout().addWidget(cleanup_splitter)

        cleanup_layout = QtWidgets.QHBoxLayout()
        cleanup_layout.setContentsMargins(4, 0, 4, 0)
        cleanup_layout.setSpacing(2)
        cleanup_widget.layout().addLayout(cleanup_layout)

        self.end_digits_button = QtWidgets.QPushButton('End Digits')
        # Below buttons need proper functions written...-----------
        self.shape_name_button = QtWidgets.QPushButton('Shape Names')
        self.deformer_name_button = QtWidgets.QPushButton('Deformer Names')

        cleanup_layout.addWidget(self.end_digits_button)
        cleanup_layout.addWidget(self.shape_name_button)
        cleanup_layout.addWidget(self.deformer_name_button)

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

        self.prefix_add_button.clicked.connect(
            partial(self.edit_prefix, True, False, False))
        self.prefix_remove_button.clicked.connect(
            partial(self.edit_prefix, False, False, True))
        self.prefix_replace_button.clicked.connect(
            partial(self.edit_prefix, False, False, True))

        self.suffix_add_button.clicked.connect(
            partial(self.edit_suffix, True, False, False))
        self.suffix_remove_button.clicked.connect(
            partial(self.edit_suffix, False, False, True))
        self.suffix_replace_button.clicked.connect(
            partial(self.edit_suffix, False, True, False))

        self.end_digits_button.clicked.connect(clear_end_digits)

        self._update_example()

    def _toggle_rename_vis(self):
        visible = self.rename_alpha_radio.isChecked()
        self.lower_radio.setVisible(visible)
        self.upper_radio.setVisible(visible)
        self.rename_start_number.setValue(int(visible))
        self.rename_start_number.setMinimum(int(visible))

    def _get_rename_settings(self):
        text = str(self.rename_line_edit.text()).strip()

        naming_method = self.rename_number_radio.isChecked()

        starting_number = self.rename_start_number.value()

        upper = True
        if naming_method is False:
            upper = self.upper_radio.isChecked()

        return text, starting_number, naming_method, upper

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
        text, starting_number, naming_method, upper = \
            self._get_rename_settings()

        if naming_method:
            index_type = True
        else:
            index_type = False

        if upper:
            case = True
        else:
            case = False

        ending = self.list_end_condition_checkbox.isChecked()

        list_renamer(
            new_name=text,
            numeric_index=index_type,
            start_number=starting_number,
            upper_case=case,
            end_name=ending
        )

    def replace_text(self):
        find_text = str(self.find_line_edit.text()).strip()
        replace_text = str(self.replace_line_edit.text()).strip()

        if self.selected_radio_button.isChecked():
            select_scope = False
        else:
            select_scope = True

        search_replace_name(
            search_input=find_text,
            replace_output=replace_text,
            hierarchy=select_scope
        )

    def edit_prefix(self, add=False, replace=False, remove=False):

        prefix = str(self.prefix_line_edit.text()).strip()

        set_prefix(input_prefix=prefix, add=add, remove=remove, replace=replace)

    def edit_suffix(self, add=False, replace=False, remove=False):

        suffix = str(self.suffix_line_edit.text()).strip()
        print suffix

        set_suffix(input_suffix=suffix, add=add, remove=remove, replace=replace)
