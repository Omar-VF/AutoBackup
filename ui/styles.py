"""
Lavish, spacious editorial luxury stylesheet for Shop AutoBackup Pro.
Primary Dominant Color: #FDFBD4 (Warm Cream / Linen Canvas)
Typography & Accents:
- #38240D (Deep Espresso)
- #713600 (Saddle Brown)
- #C05800 (Burnt Amber / Terracotta)
"""

MODERN_DARK_STYLE = """
/* ================= GLOBAL BASE ================= */
QWidget {
    background-color: #FDFBD4;
    color: #38240D;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, sans-serif;
    font-size: 13px;
    selection-background-color: #C05800;
    selection-color: #FDFBD4;
}

QMainWindow, QDialog {
    background-color: #FDFBD4;
}

/* ================= CARDS & CONTAINERS ================= */
QFrame[card="hero"] {
    background-color: #FDFBD4;
    border: 2px solid #C05800;
    border-radius: 14px;
}

QFrame[card="surface"] {
    background-color: #FDFBD4;
    border: 1.5px solid rgba(113, 54, 0, 0.35);
    border-radius: 14px;
}

QFrame[card="surface"]:hover {
    border: 1.5px solid #C05800;
}

QFrame[card="modal"] {
    background-color: #FDFBD4;
    border: 2px solid #C05800;
    border-radius: 16px;
}

QFrame[separator="true"] {
    background-color: rgba(113, 54, 0, 0.22);
    border: none;
    max-height: 1px;
}

/* In-Window Scrim Dimmer */
QWidget[role="scrim"] {
    background-color: rgba(56, 36, 13, 0.50);
}

/* ================= TYPOGRAPHY ================= */
QLabel {
    background: transparent;
    color: #38240D;
}

QLabel[role="app_title"] {
    font-size: 17px;
    font-weight: 700;
    color: #38240D;
    letter-spacing: -0.2px;
}

QLabel[role="hero_title"] {
    font-size: 21px;
    font-weight: 700;
    color: #38240D;
    letter-spacing: -0.3px;
}

QLabel[role="hero_subtitle"] {
    font-size: 13px;
    color: #713600;
}

QLabel[role="section_tag"] {
    font-size: 11px;
    font-weight: 700;
    color: #C05800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel[role="path_value"] {
    font-size: 14px;
    font-weight: 600;
    color: #38240D;
}

QLabel[role="muted"] {
    font-size: 13px;
    color: #713600;
}

/* ================= STATUS PILLS ================= */
QLabel[pill="active"] {
    background-color: rgba(192, 88, 0, 0.12);
    color: #C05800;
    border: 1.5px solid #C05800;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
    qproperty-alignment: 'AlignCenter';
}

QLabel[pill="paused"] {
    background-color: rgba(113, 54, 0, 0.12);
    color: #713600;
    border: 1.5px solid #713600;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
    qproperty-alignment: 'AlignCenter';
}

QLabel[pill="error"] {
    background-color: rgba(192, 88, 0, 0.16);
    color: #C05800;
    border: 1.5px solid #C05800;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
    qproperty-alignment: 'AlignCenter';
}

QLabel[pill="neutral"] {
    background-color: rgba(56, 36, 13, 0.05);
    color: #38240D;
    border: 1.2px solid rgba(113, 54, 0, 0.28);
    border-radius: 11px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 600;
    qproperty-alignment: 'AlignCenter';
}

/* ================= BUTTONS ================= */
QPushButton {
    background-color: rgba(56, 36, 13, 0.04);
    color: #38240D;
    border: 1.2px solid rgba(113, 54, 0, 0.35);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: rgba(113, 54, 0, 0.12);
    border-color: #713600;
    color: #38240D;
}

QPushButton:pressed {
    background-color: rgba(56, 36, 13, 0.16);
}

QPushButton:disabled {
    color: rgba(56, 36, 13, 0.3);
    background-color: rgba(56, 36, 13, 0.02);
    border-color: rgba(113, 54, 0, 0.15);
}

/* Primary Action Button (Burnt Amber Terracotta) */
QPushButton[role="primary"] {
    background-color: #C05800;
    color: #FDFBD4;
    border: 1.5px solid #C05800;
    border-radius: 9px;
    padding: 11px 24px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton[role="primary"]:hover {
    background-color: #713600;
    border-color: #713600;
    color: #FDFBD4;
}

QPushButton[role="primary"]:pressed {
    background-color: #38240D;
    border-color: #38240D;
}

/* Icon Buttons */
QPushButton[role="icon"] {
    background-color: rgba(56, 36, 13, 0.04);
    border: 1.2px solid rgba(113, 54, 0, 0.35);
    border-radius: 8px;
    padding: 7px;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
}

QPushButton[role="icon"]:hover {
    background-color: rgba(192, 88, 0, 0.12);
    border-color: #C05800;
}

QPushButton[role="icon"]:pressed {
    background-color: rgba(56, 36, 13, 0.15);
}

/* Ghost Button */
QPushButton[role="ghost"] {
    background-color: transparent;
    color: #713600;
    border: 1.2px solid transparent;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton[role="ghost"]:hover {
    background-color: rgba(113, 54, 0, 0.08);
    border-color: rgba(113, 54, 0, 0.25);
    color: #38240D;
}

/* ================= INPUTS & CONTROLS ================= */
QLineEdit, QComboBox, QTimeEdit, QSpinBox {
    background-color: #FDFBD4;
    color: #38240D;
    border: 1.2px solid rgba(113, 54, 0, 0.35);
    border-radius: 8px;
    padding: 4px 10px;
    min-height: 26px;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QTimeEdit:focus, QSpinBox:focus {
    border: 1.5px solid #C05800;
    background-color: #FDFBD4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* ================= PROGRESS BAR ================= */
QProgressBar {
    background-color: rgba(56, 36, 13, 0.08);
    border: 1px solid rgba(113, 54, 0, 0.25);
    border-radius: 5px;
    max-height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #C05800;
    border-radius: 4px;
}

/* ================= CHECKBOXES ================= */
QCheckBox {
    color: #38240D;
    font-size: 13px;
    spacing: 10px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.2px solid #713600;
    background-color: #FDFBD4;
}

QCheckBox::indicator:hover {
    border-color: #C05800;
}

QCheckBox::indicator:checked {
    background-color: #C05800;
    border-color: #38240D;
}

/* ================= TOOLTIPS & MENUS ================= */
QToolTip {
    background-color: #FDFBD4;
    color: #38240D;
    border: 1.2px solid #713600;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

QMenu {
    background-color: #FDFBD4;
    border: 1.5px solid rgba(113, 54, 0, 0.35);
    border-radius: 10px;
    padding: 8px;
}

QMenu::item {
    padding: 8px 24px 8px 14px;
    border-radius: 6px;
    color: #38240D;
    font-size: 13px;
}

QMenu::item:selected {
    background-color: #C05800;
    color: #FDFBD4;
}

QMenu::separator {
    height: 1px;
    background-color: rgba(113, 54, 0, 0.25);
    margin: 4px 6px;
}
"""
