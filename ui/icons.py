import math
from pathlib import Path
from PyQt6.QtCore import QPointF, QRectF, Qt, QSize
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
)
from PyQt6.QtWidgets import QWidget

# Exact Design Tokens from Design PDF / HTML
COLOR_BG = "#FCF7DE"          # Canvas
COLOR_DARK = "#2E1A08"        # Deep Espresso (Typography, dark cards, dark buttons)
COLOR_CARD_BG = "#F3EBC4"     # Surface cards (Source, Destination, Schedule)
COLOR_BADGE_BG = "#E8DBA6"    # Icon badge containers
COLOR_BTN_SEC = "#EFE4B8"     # Secondary header/chip buttons
COLOR_ORANGE = "#B85400"      # Primary CTA / Active indicators
COLOR_AMBER = "#8F4300"       # Source/Dest labels & icon strokes
COLOR_EYEBROW = "#F7BE72"     # Setup Needed tag
COLOR_MUTED = "#6B4E31"       # Secondary typography
COLOR_ARROW = "#B9A468"       # Dashed connection line

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ICON_PATH = ASSETS_DIR / "tethr_icon.png"


def create_app_icon(size: int = 38) -> QIcon:
    """Renders the official Tethr brand icon."""
    if ICON_PATH.exists():
        pm = QPixmap(str(ICON_PATH))
        if not pm.isNull():
            scaled = pm.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            return QIcon(scaled)

    # Fallback
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor(COLOR_DARK)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRectF(2, 2, size - 4, size - 4), size * 0.25, size * 0.25)
    painter.end()
    return QIcon(pixmap)


def create_tray_icon(status: str = "active", size: int = 32) -> QIcon:
    """Renders system tray icon with contrast container and live status pip."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Clean cream container badge
    badge_rect = QRectF(1.0, 1.0, size - 2.0, size - 2.0)
    painter.setBrush(QBrush(QColor(COLOR_BG)))
    painter.setPen(QPen(QColor(COLOR_ARROW), 1.0))
    painter.drawRoundedRect(badge_rect, size * 0.28, size * 0.28)

    # Center Tethr icon
    if ICON_PATH.exists():
        src_pm = QPixmap(str(ICON_PATH))
        if not src_pm.isNull():
            inner_size = int(size * 0.68)
            offset = int((size - inner_size) / 2)
            scaled = src_pm.scaled(
                inner_size,
                inner_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(offset, offset, scaled)

    # Live status pip in bottom-right corner
    color_map = {
        "active": COLOR_ORANGE,
        "working": COLOR_EYEBROW,
        "paused": COLOR_MUTED,
        "error": COLOR_ORANGE,
    }
    pip_color = color_map.get(status, COLOR_ORANGE)

    pip_r = size * 0.16
    pip_center = QPointF(size - pip_r - 1, size - pip_r - 1)

    painter.setBrush(QBrush(QColor(COLOR_DARK)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(pip_center, pip_r + 1.5, pip_r + 1.5)

    painter.setBrush(QBrush(QColor(pip_color)))
    painter.drawEllipse(pip_center, pip_r, pip_r)

    painter.end()
    return QIcon(pixmap)


def get_gear_icon(size: int = 18, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders clean settings gear icon matching design stroke."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

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

    p.setBrush(QBrush(QColor(color_hex)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawPath(path)

    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    p.drawEllipse(QPointF(center, center), hole_r, hole_r)
    p.end()
    return QIcon(pixmap)


def get_pause_icon(size: int = 16, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders two vertical pause bars matching design: rect x=3.5, y=2.5, w=3, h=11."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(color_hex)))
    p.setPen(Qt.PenStyle.NoPen)

    scale = size / 16.0
    p.drawRoundedRect(QRectF(3.5 * scale, 2.5 * scale, 3.0 * scale, 11.0 * scale), 1.0, 1.0)
    p.drawRoundedRect(QRectF(9.5 * scale, 2.5 * scale, 3.0 * scale, 11.0 * scale), 1.0, 1.0)
    p.end()
    return QIcon(pixmap)


def get_play_icon(size: int = 16, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders clean play triangle."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(color_hex)))
    p.setPen(Qt.PenStyle.NoPen)

    scale = size / 16.0
    path = QPainterPath()
    path.moveTo(4.5 * scale, 2.5 * scale)
    path.lineTo(13.0 * scale, 8.0 * scale)
    path.lineTo(4.5 * scale, 13.5 * scale)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return QIcon(pixmap)


def get_folder_icon(size: int = 22, color_hex: str = COLOR_AMBER) -> QIcon:
    """Renders tabbed folder icon matching SVG: d='M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    scale = size / 24.0
    pen = QPen(QColor(color_hex), 2.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    path = QPainterPath()
    path.moveTo(3 * scale, 7 * scale)
    path.lineTo(5 * scale, 5 * scale)
    path.lineTo(9 * scale, 5 * scale)
    path.lineTo(11 * scale, 7 * scale)
    path.lineTo(19 * scale, 7 * scale)
    path.lineTo(21 * scale, 9 * scale)
    path.lineTo(21 * scale, 17 * scale)
    path.lineTo(19 * scale, 19 * scale)
    path.lineTo(5 * scale, 19 * scale)
    path.lineTo(3 * scale, 17 * scale)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return QIcon(pixmap)


def get_drive_icon(size: int = 22, color_hex: str = COLOR_AMBER) -> QIcon:
    """Renders external drive icon matching SVG: rect x=3 y=6 w=18 h=12 rx=2, circle cx=17 cy=12 r=1.2, line 7 12 -> 12 12."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    scale = size / 24.0
    pen = QPen(QColor(color_hex), 2.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    p.drawRoundedRect(QRectF(3 * scale, 6 * scale, 18 * scale, 12 * scale), 2 * scale, 2 * scale)
    p.drawLine(QPointF(7 * scale, 12 * scale), QPointF(12 * scale, 12 * scale))

    p.setBrush(QBrush(QColor(color_hex)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(17 * scale, 12 * scale), 1.5 * scale, 1.5 * scale)
    p.end()
    return QIcon(pixmap)


def get_sync_icon(size: int = 18, color_hex: str = "#FFF8E6") -> QIcon:
    """Renders backup now circular sync arrow matching SVG: path d='M21 12a9 9 0 1 1-3-6.7' and d='M21 4v5h-5'."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    scale = size / 24.0
    pen = QPen(QColor(color_hex), 2.2 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Arc from (18, 5.3) around (12, 12) radius 9
    arc_rect = QRectF(3 * scale, 3 * scale, 18 * scale, 18 * scale)
    p.drawArc(arc_rect, 45 * 16, -300 * 16)

    # Arrow head
    path = QPainterPath()
    path.moveTo(16 * scale, 4 * scale)
    path.lineTo(21 * scale, 4 * scale)
    path.lineTo(21 * scale, 9 * scale)
    p.drawPath(path)
    p.end()
    return QIcon(pixmap)


def get_close_icon(size: int = 16, color_hex: str = COLOR_DARK) -> QIcon:
    """Renders close 'X' icon: M5 5l14 14M19 5L5 19."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    scale = size / 24.0
    pen = QPen(QColor(color_hex), 2.4 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap)
    p.setPen(pen)

    p.drawLine(QPointF(5 * scale, 5 * scale), QPointF(19 * scale, 19 * scale))
    p.drawLine(QPointF(19 * scale, 5 * scale), QPointF(5 * scale, 19 * scale))
    p.end()
    return QIcon(pixmap)


class DashedArrowWidget(QWidget):
    """Draws the exact connection arrow between source and destination cards from design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(72, 36)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cy = h / 2.0
        start_x = (w - 56) / 2.0 + 4.0
        end_x = start_x + 40.0

        # Dashed line
        pen = QPen(QColor(COLOR_ARROW), 2.0)
        pen.setDashPattern([3.0, 5.0])
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        p.setPen(pen)
        p.drawLine(QPointF(start_x, cy), QPointF(end_x, cy))

        # Arrow head
        pen_head = QPen(QColor(COLOR_ARROW), 2.0)
        pen_head.setCapStyle(Qt.PenCapStyle.SquareCap)
        pen_head.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        p.setPen(pen_head)

        head_path = QPainterPath()
        head_path.moveTo(end_x - 2.0, cy - 6.0)
        head_path.lineTo(end_x + 6.0, cy)
        head_path.lineTo(end_x - 2.0, cy + 6.0)
        p.drawPath(head_path)
        p.end()
