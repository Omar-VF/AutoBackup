import math
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap

# Strictly 4-color palette
COLOR_CREAM = "#FDFBD4"   # Primary dominant background & high-contrast light accents
COLOR_DARK = "#38240D"    # Deep espresso for typography, headings, dark icons
COLOR_BROWN = "#713600"   # Saddle brown for borders, secondary accents
COLOR_ORANGE = "#C05800"  # Burnt amber / terracotta for primary actions, active indicators


def create_app_icon(size: int = 64) -> QIcon:
    """Renders a sleek, modern gradient shield/disk backup icon in custom palette."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    rect = QRectF(3, 3, size - 6, size - 6)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(COLOR_ORANGE))
    gradient.setColorAt(1, QColor(COLOR_BROWN))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(COLOR_CREAM), 1.5))
    painter.drawRoundedRect(rect, size * 0.24, size * 0.24)

    # Circular sync arc
    pen = QPen(QColor(COLOR_CREAM), size * 0.08, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    center = QPointF(size / 2, size / 2)
    radius = size * 0.24
    arc_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
    painter.drawArc(arc_rect, 45 * 16, 270 * 16)

    # Arrow head
    arrow_path = QPainterPath()
    arrow_path.moveTo(center.x() + radius - size * 0.08, center.y() - size * 0.12)
    arrow_path.lineTo(center.x() + radius + size * 0.08, center.y())
    arrow_path.lineTo(center.x() + radius - size * 0.08, center.y() + size * 0.12)
    painter.strokePath(arrow_path, pen)

    painter.end()
    return QIcon(pixmap)


def create_tray_icon(status: str = "active", size: int = 32) -> QIcon:
    """Renders system tray status icons in the custom palette."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    color_map = {
        "active": (COLOR_ORANGE, COLOR_BROWN),
        "working": (COLOR_CREAM, COLOR_ORANGE),
        "paused": (COLOR_BROWN, COLOR_DARK),
        "error": (COLOR_ORANGE, COLOR_BROWN),
    }
    c1, c2 = color_map.get(status, (COLOR_ORANGE, COLOR_BROWN))

    bg_rect = QRectF(2, 2, size - 4, size - 4)
    painter.setBrush(QBrush(QColor(COLOR_CREAM)))
    painter.setPen(QPen(QColor(COLOR_BROWN), 1.4))
    painter.drawRoundedRect(bg_rect, size * 0.28, size * 0.28)

    center_rect = QRectF(size * 0.28, size * 0.28, size * 0.44, size * 0.44)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(c1))
    gradient.setColorAt(1, QColor(c2))

    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center_rect)

    painter.end()
    return QIcon(pixmap)


def get_gear_icon(size: int = 18, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders a crisp vector gear icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    center = size / 2.0
    outer_r = size * 0.44
    inner_r = size * 0.32
    hole_r = size * 0.16
    teeth = 6

    path = QPainterPath()
    for i in range(teeth):
        angle = (2 * math.pi / teeth) * i
        step = (2 * math.pi / teeth)

        a1 = angle - step * 0.22
        a2 = angle - step * 0.12
        a3 = angle + step * 0.12
        a4 = angle + step * 0.22

        p1 = QPointF(center + inner_r * math.cos(a1), center + inner_r * math.sin(a1))
        p2 = QPointF(center + outer_r * math.cos(a2), center + outer_r * math.sin(a2))
        p3 = QPointF(center + outer_r * math.cos(a3), center + outer_r * math.sin(a3))
        p4 = QPointF(center + inner_r * math.cos(a4), center + inner_r * math.sin(a4))

        if i == 0:
            path.moveTo(p1)
        else:
            path.lineTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p4)

    path.closeSubpath()

    painter.setBrush(QBrush(QColor(color_hex)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(path)

    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    painter.drawEllipse(QPointF(center, center), hole_r, hole_r)

    painter.end()
    return QIcon(pixmap)


def get_pause_icon(size: int = 18, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders two crisp rounded vertical bars."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.setPen(Qt.PenStyle.NoPen)

    bar_w = max(2.5, size * 0.18)
    bar_h = size * 0.52
    top = (size - bar_h) / 2.0
    spacing = size * 0.16

    x1 = (size / 2.0) - bar_w - (spacing / 2.0)
    x2 = (size / 2.0) + (spacing / 2.0)

    painter.drawRoundedRect(QRectF(x1, top, bar_w, bar_h), bar_w * 0.4, bar_w * 0.4)
    painter.drawRoundedRect(QRectF(x2, top, bar_w, bar_h), bar_w * 0.4, bar_w * 0.4)

    painter.end()
    return QIcon(pixmap)


def get_play_icon(size: int = 18, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders a clean play triangle."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.setPen(Qt.PenStyle.NoPen)

    path = QPainterPath()
    left = size * 0.32
    right = size * 0.74
    top = size * 0.24
    bot = size * 0.76
    mid_y = size * 0.50

    path.moveTo(left, top)
    path.lineTo(right, mid_y)
    path.lineTo(left, bot)
    path.closeSubpath()

    painter.drawPath(path)
    painter.end()
    return QIcon(pixmap)


def get_folder_icon(size: int = 20, color_hex: str = COLOR_ORANGE) -> QIcon:
    """Renders a modern sleek folder icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.setPen(Qt.PenStyle.NoPen)

    path = QPainterPath()
    x = size * 0.1
    y = size * 0.22
    w = size * 0.8
    h = size * 0.58

    path.moveTo(x, y + 2)
    path.lineTo(x + w * 0.38, y + 2)
    path.lineTo(x + w * 0.48, y + h * 0.22)
    path.lineTo(x + w, y + h * 0.22)
    path.lineTo(x + w, y + h)
    path.lineTo(x, y + h)
    path.closeSubpath()

    painter.drawRoundedRect(QRectF(x, y + h * 0.16, w, h * 0.84), 3, 3)
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def get_drive_icon(size: int = 20, color_hex: str = COLOR_BROWN) -> QIcon:
    """Renders a modern sleek external hard drive icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    rect = QRectF(size * 0.1, size * 0.25, size * 0.8, size * 0.5)
    painter.setBrush(QBrush(QColor(COLOR_CREAM)))
    painter.setPen(QPen(QColor(color_hex), 1.6))
    painter.drawRoundedRect(rect, 4, 4)

    # Activity LED in Orange
    painter.setBrush(QBrush(QColor(COLOR_ORANGE)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QPointF(size * 0.76, size * 0.5), size * 0.08, size * 0.08)

    painter.end()
    return QIcon(pixmap)


def get_sync_icon(size: int = 16, color_hex: str = COLOR_CREAM) -> QIcon:
    """Renders an instant sync/flash icon for primary button."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color_hex), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    c = size / 2.0
    r = size * 0.34
    rect = QRectF(c - r, c - r, r * 2, r * 2)
    painter.drawArc(rect, 30 * 16, 280 * 16)

    # Arrow tip
    p1 = QPointF(c + r, c - 2)
    painter.drawLine(p1, QPointF(c + r - 3, c - 6))
    painter.drawLine(p1, QPointF(c + r + 3, c - 5))

    painter.end()
    return QIcon(pixmap)
