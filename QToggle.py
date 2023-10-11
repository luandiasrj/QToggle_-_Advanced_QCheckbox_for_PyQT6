"""
Author: Luan Dias - https://github.com/luandiasrj
Url: https://github.com/luandiasrj/QToggle_-_Advanced_QCheckbox_for_PyQT6

This code implements a custom QToggle class, which is a toggle switch derived
from QCheckBox. The QToggle class features customizable colors, and properties.
It includes smooth transitions when toggling between states.

The custom properties include:

    bg_color: background color of the toggle
    circle_color: color of the circle inside the toggle
    active_color: color of the background when the toggle is checked
    disabled_color: color of the toggle when it's disabled
    text_color: color of the text

Main functions and methods in the class include:

    init: Initializes the QToggle object with default colors and settings
    setDuration: Set the duration for the animation
    update_pos_color: Updates the circle position and background color
    start_transition: Starts the transition animation when the state changes
    create_animation: Creates the circle position animation
    create_bg_color_animation: Creates the background color animation
    sizeHint: Provides the recommended size for the toggle
    hitButton: Determines if the mouse click is inside the toggle area
    paintEvent: Handles the custom painting of the toggle

The example demonstrates how to use the QToggle class by creating three
different toggles with various settings such as custom height, colors, and font.
"""

from PyQt6.QtCore import Qt, QRect, pyqtProperty, QPropertyAnimation, QPoint, \
    QEasingCurve
from PyQt6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QBrush, \
    QPen, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout


class QToggle(QCheckBox):
    bg_color = pyqtProperty(
        QColor, lambda self: self._bg_color,
        lambda self, col: setattr(self, '_bg_color', col))
    circle_color = pyqtProperty(
        QColor, lambda self: self._circle_color,
        lambda self, col: setattr(self, '_circle_color', col))
    active_color = pyqtProperty(
        QColor, lambda self: self._active_color,
        lambda self, col: setattr(self, '_active_color', col))
    disabled_color = pyqtProperty(
        QColor, lambda self: self._disabled_color,
        lambda self, col: setattr(self, '_disabled_color', col))
    text_color = pyqtProperty(
        QColor, lambda self: self._text_color,
        lambda self, col: setattr(self, '_text_color', col))

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_color, self._circle_color, self._active_color, \
            self._disabled_color, self._text_color = QColor("#0BF"), \
            QColor("#DDD"), QColor('#777'), QColor("#CCC"), QColor("#000")
        self._circle_pos, self._intermediate_bg_color = None, None
        self.setFixedHeight(18)
        self._animation_duration = 500  # milliseconds
        self.stateChanged.connect(self.start_transition)
        self._user_checked = False  # Introduced flag to check user-initiated changes

    circle_pos = pyqtProperty(
        float, lambda self: self._circle_pos,
        lambda self, pos: (setattr(self, '_circle_pos', pos), self.update()))
    intermediate_bg_color = pyqtProperty(
        QColor, lambda self: self._intermediate_bg_color,
        lambda self, col: setattr(self, '_intermediate_bg_color', col))

    def setDuration(self, duration: int):
        """
        Set the duration for the animation.
        :param duration: Duration in milliseconds.
        """
        self._animation_duration = duration

    def update_pos_color(self, checked=None):
        self._circle_pos = self.height() * (1.1 if checked else 0.1)
        if self.isChecked():
            self._intermediate_bg_color = self._active_color
        else:
            self._intermediate_bg_color = self._bg_color

    def start_transition(self, state):
        if not self._user_checked:  # Skip animation if change isn't user-initiated
            self.update_pos_color(state)
            return
        for anim in [self.create_animation, self.create_bg_color_animation]:
            animation = anim(state)
            animation.start()
        self._user_checked = False  # Reset the flag after animation starts

    def mousePressEvent(self, event):
        self._user_checked = True  # Set flag when user manually clicks the toggle
        super().mousePressEvent(event)

    def create_animation(self, state):
        return self._create_common_animation(
            state, b'circle_pos', self.height() * 0.1, self.height() * 1.1)

    def create_bg_color_animation(self, state):
        return self._create_common_animation(
            state, b'intermediate_bg_color', self._bg_color, self._active_color)

    def _create_common_animation(self, state, prop, start_val, end_val):
        animation = QPropertyAnimation(self, prop, self)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.setDuration(self._animation_duration)
        animation.setStartValue(start_val if state else end_val)
        animation.setEndValue(end_val if state else start_val)
        return animation

    def showEvent(self, event):
        super().showEvent(event)  # Ensure to call the super class's implementation
        self.update_pos_color(self.isChecked())

    def resizeEvent(self, event):
        self.update_pos_color(self.isChecked())

    def sizeHint(self):
        size = super().sizeHint()
        text_width = QFontMetrics(
            self.font()).boundingRect(self.text()).width()
        size.setWidth(int(self.height() * 2 + text_width * 1.075))
        return size

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        circle_color = QColor(
            self.disabled_color if not self.isEnabled() else self.circle_color)
        bg_color = QColor(
            self.disabled_color if not self.isEnabled() else
            self.intermediate_bg_color)
        text_color = QColor(
            self.disabled_color if not self.isEnabled() else self.text_color)

        bordersradius = self.height() / 2
        togglewidth = self.height() * 2
        togglemargin = self.height() * 0.3
        circlesize = self.height() * 0.8

        bg_path = QPainterPath()
        bg_path.addRoundedRect(
            0, 0, togglewidth, self.height(), bordersradius, bordersradius)
        painter.fillPath(bg_path, QBrush(bg_color))

        circle = QPainterPath()
        circle.addEllipse(
            self.circle_pos, self.height() * 0.1, circlesize, circlesize)
        painter.fillPath(circle, QBrush(circle_color))

        painter.setPen(QPen(QColor(text_color)))
        painter.setFont(self.font())
        text_rect = QRect(int(togglewidth + togglemargin), 0, self.width() -
                          int(togglewidth + togglemargin), self.height())
        text_rect.adjust(
            0, (self.height() - painter.fontMetrics().height()) // 2, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft |
                         Qt.AlignmentFlag.AlignVCenter, self.text())
        painter.end()


if __name__ == '__main__':
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()

    checkbox0 = QToggle()
    checkbox0.setFixedHeight(12)
    layout.addWidget(checkbox0)

    checkbox1 = QToggle()
    checkbox1.setText('Checkbox 1 - Disabled')
    checkbox1.setEnabled(False)
    layout.addWidget(checkbox1)

    checkbox2 = QToggle()
    checkbox2.setText('Checkbox 2 - Checked, custom height, animation duration, colors and font')
    checkbox2.setFixedHeight(24)
    checkbox2.setFont(QFont('Segoe Print', 10))
    checkbox2.setStyleSheet("QToggle{"
                            "qproperty-bg_color:#FAA;"
                            "qproperty-circle_color:#DDF;"
                            "qproperty-active_color:#AAF;"
                            "qproperty-disabled_color:#777;"
                            "qproperty-text_color:#A0F;}")
    checkbox2.setDuration(2000)
    checkbox2.setChecked(True)
    layout.addWidget(checkbox2)

    window.setLayout(layout)
    window.show()
    app.exec()
