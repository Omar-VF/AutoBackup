from PyQt6.QtCore import QRectF, QPropertyAnimation, pyqtProperty, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen
from PyQt6.QtWidgets import QAbstractButton

class ToggleSwitch(QAbstractButton):
    """
    Toggle switch matching the exact design specifications:
    - 40px width x 22px height, 7px border radius
    - On: background #B85400, thumb #FFF8E6 (16x16, 4px radius)
    - Off: background #CDBE8C, thumb #FCF7DE (16x16, 4px radius)
    """

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._thumb_pos = 1.0 if checked else 0.0
        self._anim = QPropertyAnimation(self, b"thumb_pos", self)
        self._anim.setDuration(120)
        self.toggled.connect(self._start_anim)

    @pyqtProperty(float)
    def thumb_pos(self):
        return self._thumb_pos

    @thumb_pos.setter
    def thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()

    def _start_anim(self, checked):
        self._anim.stop()
        self._anim.setStartValue(self._thumb_pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        r = 7.0

        # Background color interpolation
        # Off: #CDBE8C (205, 190, 140) -> On: #B85400 (184, 84, 0)
        c_off = QColor("#CDBE8C")
        c_on = QColor("#B85400")
        bg_r = int(c_off.red() + (c_on.red() - c_off.red()) * self._thumb_pos)
        bg_g = int(c_off.green() + (c_on.green() - c_off.green()) * self._thumb_pos)
        bg_b = int(c_off.blue() + (c_on.blue() - c_off.blue()) * self._thumb_pos)

        p.setBrush(QBrush(QColor(bg_r, bg_g, bg_b)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        # Thumb
        thumb_size = 16.0
        thumb_padding = 3.0
        thumb_min_x = thumb_padding
        thumb_max_x = w - thumb_size - thumb_padding
        curr_x = thumb_min_x + (thumb_max_x - thumb_min_x) * self._thumb_pos
        curr_y = (h - thumb_size) / 2.0

        # Thumb color: Off: #FCF7DE -> On: #FFF8E6
        t_off = QColor("#FCF7DE")
        t_on = QColor("#FFF8E6")
        th_r = int(t_off.red() + (t_on.red() - t_off.red()) * self._thumb_pos)
        th_g = int(t_off.green() + (t_on.green() - t_off.green()) * self._thumb_pos)
        th_b = int(t_off.blue() + (t_on.blue() - t_off.blue()) * self._thumb_pos)

        p.setBrush(QBrush(QColor(th_r, th_g, th_b)))
        p.drawRoundedRect(QRectF(curr_x, curr_y, thumb_size, thumb_size), 4.0, 4.0)
        p.end()
