import maya.cmds as cmds
from string import ascii_uppercase

LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}


def list_renamer(new_name, index_type='number', start_number=1,
                 end_name=False, selection=True, list_input=[]):
    """
    Renamer tool for renaming lists of objects.  Default works based off
    selection, but can take a list parameter when function is passed with larger
    tools and functions.

    Args:
        new_name (str): Name to assign to object list. Must include at least
            one '#'.
        index_type (str): Assign numeric or alphanumeric values to the padding
            of renamed objects in the list.
        start_number (int): Assign starting index for the numeric renaming.  In
            alphanumeric, it will apply to the corresponding letter position.
            (ex. 2 = 'B')
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
        name_list = cmds.ls(selection=True)
    else:
        name_list = list_input
    index_start = max(0, start_number)

    if '#' not in new_name:
        cmds.warning('Could not find any "#" in name.')

    pad_replace = ''
    number_padding = new_name.count('#')
    for i in range(number_padding):
        pad_replace = pad_replace + '#'

    new_name_list = []
    # Numeric renaming
    if index_type == 'number':
        index = index_start

        for i in name_list:
            padded_index = str(index).zfill(number_padding)
            cmds.rename(i, new_name.replace(pad_replace, padded_index))
            new_name_list.append(new_name.replace(pad_replace, padded_index))
            index = index + 1

    # Alphanumeric renaming
    elif index_type == 'alpha' or index_type == 'letters':
        # If index is not 0, the index will be changed to start letters at
        # appropriate alphanumeric count
        if index_start > 0:
            index = index_start
        else:
            index = 1

        for i in name_list:
            padded_index = LETTERS_INDEX[index]
            cmds.rename(i, new_name.replace(pad_replace, padded_index))
            new_name_list.append(new_name.replace(pad_replace, padded_index))
            index = index + 1

    else:
        cmds.warning('Invalid argument given for the index_type.  Use "number",'
                     ' "alpha", or "letters"')
        return

    # After indexes are all named, check if last object should be an 'end'
    if end_name:
        new_name_list[-1] = cmds.rename(new_name_list[-1],
                                        new_name.replace(pad_replace, 'END'))

    return new_name_list


def set_prefix(input_prefix, add=False, replace=False, remove=False,
               selection=True, list_input=[]):
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
        selection (bool): Confirm that the function performs based on the 
            selection list. 
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
    if selection:
        name_list = cmds.ls(selection=True)
    else:
        name_list = list_input

    if add:
        for i in name_list:
            cmds.rename(i, '%s_%s' % (input_prefix, i))

    if replace:
        kill_length_list = []
        for obj in name_list:
            kill_length = obj.find('_')
            kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            cmds.rename(i, i.replace(i[0:kill_length_list[number]], input_prefix))
            number = number + 1

    if remove:
        kill_length_list = []
        for obj in name_list:
            kill_length = obj.find('_')
            kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            if i[0] == '_':
                cmds.rename(i, i[1:])
            else:
                cmds.rename(i, i.replace(i[0:(kill_length_list[number] + 1)],
                                         ''))
            number = number + 1


def set_suffix(input_suffix, add=False, replace=False, remove=False,
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
        name_list = cmds.ls(selection=True)
    else:
        name_list = list_input

    name_return_list = []

    if add:
        for i in name_list:
            new_name = cmds.rename(i, '%s_%s' % (i, input_suffix))
            name_return_list.append(new_name)

    if replace:
        kill_length_list = []
        for obj in name_list:
            kill_length = obj.rfind('_')
            kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            new_name = cmds.rename(i, i.replace(i[kill_length_list[number]:],
                                                input_suffix))
            name_return_list.append(new_name)
            number = number + 1

    if remove:
        kill_length_list = []
        for obj in name_list:
            kill_length = obj.rfind('_')
            kill_length_list.append(kill_length)

        number = 0
        for i in name_list:
            if i[kill_length_list[number]:] == '_':
                cmds.rename(i, i[0:kill_length_list[number]])
            else:
                new_name = \
                    cmds.rename(i, i.replace(i[kill_length_list[number]:], ''))
                name_return_list.append(new_name)
            number = number + 1

    return name_return_list


def search_replace_name(search_input, replace_output, scope='selection',
                        input_object=[]):
    """
    Python equivalent of the mel searchReplaceNames procedure.  Created to work
    with GUIs and python-written scripts.

    Args:
        search_input (str): String to search for that will be replaced.
        replace_output (str): String used to replace the input string.
        scope (str): Declare the range/scope of the procedure.  Default is only
            the 'selection', but can also take 'hierarchy'.
        input_object (list[str]): Allows funciton to work based on a provided
            list.  If nothing given, selection is assumed.

    """
    name_return_list = []
    if scope == 'selection':
        if input_object:
            selection = input_object
        else:
            selection = cmds.ls(selection=True)
        for obj in selection:
            if search_input in obj:
                new_name = cmds.rename(obj, obj.replace
                                       (search_input, replace_output))
                name_return_list.append(new_name)

    elif scope == 'hierarchy':
        if input_object:
            hierarchy = cmds.listRelatives(input_object) \
                        + cmds.ls(selection=True)
        else:
            hierarchy = cmds.listRelatives(cmds.ls(selection=True)) \
                        + cmds.ls(selection=True)
        for obj in hierarchy:
            if search_input in obj:
                new_name = cmds.rename(obj, obj.replace
                                       (search_input, replace_output))
                name_return_list.append(new_name)

    else:
        cmds.error('Incorrect scope given!  Use "selection" or "hierarchy".')

    return name_return_list


def clear_end_digits(input_object=[]):
    name_return_list = []
    if input_object:
        for obj in input_object:
            num = None
            try:
                num = int(obj[-1])
            except ValueError:
                pass
            if num:
                new_name = cmds.rename(obj, obj[0:-1])
                name_return_list.append(new_name)
    else:
        input_object = cmds.ls(selection=True)
        for obj in input_object:
            num = None
            try:
                num = int(obj[-1])
            except ValueError:
                pass
            if num:
                new_name = cmds.rename(obj, obj[0:-1])
                name_return_list.append(new_name)
    return name_return_list
