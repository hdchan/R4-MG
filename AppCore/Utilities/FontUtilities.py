import os

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette

from R4UI import Label


def apply_font_style(label: Label, custom_font_path: str, font_size: int, font_color: str):
    # 1. Set Color Palette
    palette = label.palette()
    palette.setColor(QPalette.ColorRole.WindowText, QColor(font_color))
    label.setPalette(palette)

    # 2. Add Font via Absolute Path
    if custom_font_path and os.path.exists(custom_font_path):
        abs_path = os.path.abspath(custom_font_path)
        # Call as a static method
        font_id = QFontDatabase.addApplicationFont(abs_path)

        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                label.setFont(QFont(families[0], font_size))
                return

    # 3. Fallback to Default
    current_font = label.font()
    current_font.setPointSize(font_size)
    label.setFont(current_font)
