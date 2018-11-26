from PySide2 import QtWidgets, QtCore, QtGui


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
