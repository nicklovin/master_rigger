"""

The __init__ file that allows the whole directory to work as a full rigging
module. This file will also be used to store the global variables, dictionaries,
lists, and other absolutely necessary pieces that are universal to the rig
module.

This Auto-Rigging module system was made as a practice exercise in python
scripting and system module building.  It was also made in part for the benefit
of 3D animation students for the Rochester Institute of Technology, School of
Film & Animation.  This is an unsponsored project, therefore it will be edited
and will be debugged only at the convenience of the writer.  Edits to this
program may be made on an individual basis, but must not discredit the original
writer, Nicholas Love, for the work put in to write the module.  The code will
be open source to the students at RIT for the educational purposes, and
otherwise may not be spread or used without permission in writing/email by the
writer.

For additional troubleshooting and questions, please contact me at:
nicklove.productions@gmail.com

"""
from string import ascii_uppercase

LETTERS_INDEX = {index: letter for index, letter in
                 enumerate(ascii_uppercase, start=1)}

attributes = ['.tx', '.ty', '.tz',
              '.rx', '.ry', '.rz',
              '.sx', '.sy', '.sz',
              '.v']

ROTATE_ORDER = {
    'xyz': 0,
    'yzx': 1,
    'zxy': 2,
    'xzy': 3,
    'yxz': 4,
    'zyx': 5
}