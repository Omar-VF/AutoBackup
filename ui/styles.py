"""
Tethr Luxury Editorial Design Stylesheet.
Exactly matches the design specifications from design/Tethr Redesign.html & design/Tethr Redesign.pdf.

Colors:
- Canvas: #FCF7DE
- Deep Espresso: #2E1A08
- Surface Cards: #F3EBC4
- Badges: #E8DBA6
- Secondary Buttons / Chips: #EFE4B8
- Primary CTA / Active Indicators: #B85400
- Source/Dest Tags: #8F4300
- Eyebrow Tag: #F7BE72
- Muted Labels: #6B4E31
- Inactive summary pills: #E4D8A3 (text: #5E4426)
"""

TETHR_DESIGN_STYLE = """
/* ================= GLOBAL BASE ================= */
QWidget {
    background-color: #FCF7DE;
    color: #2E1A08;
    font-family: "Manrope", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    selection-background-color: #B85400;
    selection-color: #FFF8E6;
}

QMainWindow, QDialog {
    background-color: #FCF7DE;
}

/* ================= CARDS & CONTAINERS ================= */
QFrame[card="hero"] {
    background-color: #2E1A08;
    border: none;
    border-radius: 12px;
}

QFrame[card="surface"] {
    background-color: #F3EBC4;
    border: none;
    border-radius: 12px;
}

QFrame[card="modal"] {
    background-color: #FCF7DE;
    border: none;
    border-radius: 14px;
}

/* In-Window Scrim Dimmer */
QWidget[role="scrim"] {
    background-color: rgba(46, 26, 8, 0.58);
}

/* ================= TYPOGRAPHY ================= */
QLabel {
    background: transparent;
    color: #2E1A08;
}

/* App Header Title */
QLabel[role="app_title"] {
    font-family: "Instrument Serif", Georgia, serif;
    font-size: 28px;
    font-weight: 400;
    color: #2E1A08;
    letter-spacing: -0.01em;
}

/* Hero Section Typography */
QLabel[role="hero_tag"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.14em;
    color: #F7BE72;
}

QLabel[role="hero_title"] {
    font-family: "Instrument Serif", Georgia, serif;
    font-size: 46px;
    font-weight: 400;
    color: #FCF7DE;
    letter-spacing: -0.02em;
}

QLabel[role="hero_subtitle"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 15px;
    font-weight: 500;
    line-height: 1.55;
    color: #D9C9A6;
}

QLabel[role="hero_note"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: #C9B791;
}

/* Surface Card Typography */
QLabel[role="card_tag"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.12em;
    color: #8F4300;
}

QLabel[role="card_title"] {
    font-family: "Instrument Serif", Georgia, serif;
    font-size: 26px;
    font-weight: 400;
    color: #2E1A08;
}

QLabel[role="card_status"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #6B4E31;
}

/* Schedule Summary Typography */
QLabel[role="summary_tag"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.12em;
    color: #6B4E31;
}

QLabel[role="summary_val"] {
    font-family: "Instrument Serif", Georgia, serif;
    font-size: 26px;
    font-weight: 400;
    color: #2E1A08;
}

/* Footer Typography */
QLabel[role="footer_text"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #6B4E31;
}

/* Modal Typography */
QLabel[role="modal_title"] {
    font-family: "Instrument Serif", Georgia, serif;
    font-size: 44px;
    font-weight: 400;
    color: #2E1A08;
    letter-spacing: -0.02em;
}

QLabel[role="modal_subtitle"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #6B4E31;
}

QLabel[role="section_label"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.12em;
    color: #A04800;
}

QLabel[role="field_note"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: #6B4E31;
}

QLabel[role="input_label"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #6B4E31;
}

QLabel[role="switch_label"] {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #2E1A08;
}

/* ================= BUTTONS ================= */
/* Header Buttons (Pause, Settings) */
QPushButton[role="header_btn"] {
    background-color: #EFE4B8;
    border: none;
    border-radius: 7px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}
QPushButton[role="header_btn"]:hover {
    background-color: #E5D8A5;
}
QPushButton[role="header_btn"]:pressed {
    background-color: #DCCF9B;
}

/* Hero 'Back up now' Button */
QPushButton[role="hero_btn"] {
    background-color: #B85400;
    color: #FFF8E6;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 16px;
    font-weight: 700;
    border: none;
    border-radius: 7px;
    padding: 16px 28px;
}
QPushButton[role="hero_btn"]:hover {
    background-color: #A34A00;
}
QPushButton[role="hero_btn"]:disabled {
    background-color: #B85400;
    opacity: 0.45;
    color: rgba(255, 248, 230, 0.65);
}

/* Dark Action Buttons ('Choose folder', 'Choose drive') */
QPushButton[role="dark_btn"] {
    background-color: #2E1A08;
    color: #FCF7DE;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 7px;
    padding: 11px 20px;
}
QPushButton[role="dark_btn"]:hover {
    background-color: #42270D;
}
QPushButton[role="dark_btn"]:pressed {
    background-color: #1F1105;
}

/* Modal Save Settings Button */
QPushButton[role="save_btn"] {
    background-color: #B85400;
    color: #FFF8E6;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 7px;
    padding: 14px 28px;
}
QPushButton[role="save_btn"]:hover {
    background-color: #A34A00;
}
QPushButton[role="save_btn"]:pressed {
    background-color: #8F4300;
}

/* Underline Link Buttons ('Open backup folder', 'Cancel') */
QPushButton[role="link_btn"] {
    background: transparent;
    color: #A04800;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 13px;
    font-weight: 700;
    border: none;
    text-decoration: underline;
}
QPushButton[role="link_btn"]:hover {
    color: #B85400;
}

QPushButton[role="cancel_btn"] {
    background: transparent;
    color: #2E1A08;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 14px;
    font-weight: 700;
    border: none;
    text-decoration: underline;
}
QPushButton[role="cancel_btn"]:hover {
    color: #42270D;
}

/* Modal Close 'X' Button */
QPushButton[role="close_btn"] {
    background: transparent;
    border: none;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    border-radius: 6px;
}
QPushButton[role="close_btn"]:hover {
    background-color: rgba(46, 26, 8, 0.08);
}

/* Chip Buttons (Frequency, Delete After, Days) */
QPushButton[role="chip"] {
    background-color: #EFE4B8;
    color: #2E1A08;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-radius: 7px;
    padding: 9px 0;
    min-height: 18px;
}
QPushButton[role="chip"]:hover {
    background-color: #E6D9A9;
}
QPushButton[role="chip"]:checked {
    background-color: #2E1A08;
    color: #FCF7DE;
    font-weight: 700;
}

QPushButton[role="day_chip"] {
    background-color: #EFE4B8;
    color: #2E1A08;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 12px;
    font-weight: 700;
    border: none;
    border-radius: 7px;
    padding: 9px 0;
}
QPushButton[role="day_chip"]:hover {
    background-color: #E6D9A9;
}
QPushButton[role="day_chip"]:checked {
    background-color: #B85400;
    color: #FFF8E6;
}

/* Day Badges in Schedule Summary Card */
QLabel[role="summary_day_on"] {
    background-color: #B85400;
    color: #FFF8E6;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 11px;
    font-weight: 700;
    border-radius: 7px;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    qproperty-alignment: AlignCenter;
}

QLabel[role="summary_day_off"] {
    background-color: #E4D8A3;
    color: #5E4426;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 11px;
    font-weight: 700;
    border-radius: 7px;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    qproperty-alignment: AlignCenter;
}

/* ================= INPUTS & CONTROLS ================= */
QTimeEdit, QLineEdit, QSpinBox, QComboBox {
    background-color: #EFE4B8;
    color: #2E1A08;
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 15px;
    font-weight: 700;
    border: none;
    border-radius: 7px;
    padding: 10px 14px;
    min-height: 22px;
}

QTimeEdit::up-button, QTimeEdit::down-button,
QSpinBox::up-button, QSpinBox::down-button {
    width: 0px;
    height: 0px;
    border: none;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

/* QScrollArea clean styling */
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #E8DBA6;
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# Alias for backwards compatibility
MODERN_DARK_STYLE = TETHR_DESIGN_STYLE
