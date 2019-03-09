from PySide2 import QtWidgets, QtCore, QtGui

NORMAL, DOWN, DISABLED = 1, 2, 3
INNER, OUTER = 1, 2


class DT_Button(QtWidgets.QPushButton):
    _pens_text = QtGui.QPen(QtGui.QColor(202, 207, 210), 1, QtCore.Qt.SolidLine)
    _pens_shadow = QtGui.QPen(QtGui.QColor(9, 10, 12), 1, QtCore.Qt.SolidLine)
    _pens_border = QtGui.QPen(QtGui.QColor(9, 10, 12), 1, QtCore.Qt.SolidLine)
    _pens_clear = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1, QtCore.Qt.SolidLine)

    _pens_text_disabled = QtGui.QPen(QtGui.QColor(102, 107, 110), 1, QtCore.Qt.SolidLine)
    _pens_shadow_disabled = QtGui.QPen(QtGui.QColor(102, 107, 110), 1,
                                       QtCore.Qt.SolidLine)

    _brush_clear = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    _brush_border = QtGui.QBrush(QtGui.QColor(9, 10, 12))

    _gradient = {
        NORMAL: {},
        DOWN: {},
        DISABLED: {}
    }

    inner_gradient = QtGui.QLinearGradient(0, 3, 0, 24)
    inner_gradient.setColorAt(0, QtGui.QColor(53, 57, 60))
    inner_gradient.setColorAt(1, QtGui.QColor(33, 34, 36))
    _gradient[NORMAL][INNER] = QtGui.QBrush(inner_gradient)

    outer_gradient = QtGui.QLinearGradient(0, 3, 0, 24)
    outer_gradient.setColorAt(0, QtGui.QColor(69, 73, 76))
    outer_gradient.setColorAt(1, QtGui.QColor(17, 18, 20))
    _gradient[NORMAL][OUTER] = QtGui.QBrush(outer_gradient)

    inner_gradient_down = QtGui.QLinearGradient(0, 3, 0, 24)
    inner_gradient_down.setColorAt(0, QtGui.QColor(20, 21, 23))
    inner_gradient_down.setColorAt(1, QtGui.QColor(48, 49, 51))
    _gradient[DOWN][INNER] = QtGui.QBrush(inner_gradient_down)

    outer_gradient_down = QtGui.QLinearGradient(0, 3, 0, 24)
    outer_gradient_down.setColorAt(0, QtGui.QColor(36, 37, 39))
    outer_gradient_down.setColorAt(1, QtGui.QColor(32, 33, 35))
    _gradient[DOWN][OUTER] = QtGui.QBrush(outer_gradient_down)

    inner_gradient_disabled = QtGui.QLinearGradient(0, 3, 0, 24)
    inner_gradient_disabled.setColorAt(0, QtGui.QColor(33, 37, 40))
    inner_gradient_disabled.setColorAt(1, QtGui.QColor(13, 14, 16))
    _gradient[DISABLED][INNER] = QtGui.QBrush(inner_gradient_disabled)

    outer_gradient_disabled = QtGui.QLinearGradient(0, 3, 0, 24)
    outer_gradient_disabled.setColorAt(0, QtGui.QColor(49, 53, 56))
    outer_gradient_disabled.setColorAt(1, QtGui.QColor(9, 10, 12))
    _gradient[DISABLED][OUTER] = QtGui.QBrush(outer_gradient_disabled)

    def __init__(self, *args, **kwargs):
        QtWidgets.QPushButton.__init__(self, *args, **kwargs)
        self.setFixedHeight(27)

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setFamily('Calibri')
        self.setFont(font)

        self.font_metrics = QtGui.QFontMetrics(font)
        self.radius = 5

    def paintEvent(self, event):  # Name ignores PEP8 to override previous function
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        radius = self.radius

        gradient = self._gradient[NORMAL]
        offset = 0
        if self.isDown():
            gradient = self._gradient[DOWN]
            offset = 1
        elif not self.isEnabled():
            gradient = self._gradient[DISABLED]

        painter.setBrush(self._brush_border)
        painter.setPen(self._pens_clear)
        painter.drawRoundedRect(QtCore.QRect(
                x+1, y+1, width-1, height-1), radius, radius
        )

        painter.setPen(self._pens_clear)

        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(QtCore.QRect(
                x+2, y+2, width-3, height-3), radius, radius
        )

        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(
            QtCore.QRect(x + 2, y + 2, width - 5, height - 5), radius-1, radius-1
        )

        # Draw Text

        text = self.text()
        font = self.font()

        text_width = self.font_metrics.width(text)
        text_height = font.pointSize()

        text_path = QtGui.QPainterPath()
        text_path.addText((width-text_width)/2, height-((height-text_height)/2)-1+offset, font, text)

        alignment = (QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        if self.isEnabled():
            painter.setPen(self._pens_shadow)
            painter.drawPath(text_path)

            painter.setPen(self._pens_text)
            painter.drawText(x, y+offset, width, height, alignment, text)
        else:
            painter.setPen(self._pens_shadow_disabled)
            painter.drawPath(text_path)

            painter.setPen(self._pens_text_disabled)
            painter.drawText(x, y + offset, width, height, alignment, text)


class DT_ButtonThin(DT_Button):
    def __init__(self, *args, **kwargs):
        DT_Button.__init__(self, *args, **kwargs)
        self.setFixedHeight(22)
        self.radius = 10
