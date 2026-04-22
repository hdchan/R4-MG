import sys
from PySide6.QtWidgets import (QApplication, QTableView, QStyledItemDelegate, 
                               QHeaderView, QStyle)
from PySide6.QtGui import QPainter, QColor, QFontMetrics, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSize

class CustomHeader(QHeaderView):
    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        # Custom color for the first column vs others
        bg_color = QColor("#E74C3C") if logicalIndex == 0 else QColor("#34495E")
        
        painter.fillRect(rect, bg_color)
        painter.setPen(QColor("white"))
        
        # Get the text from the model
        # text = self.model().headerData(logicalIndex, Qt.Horizontal)
        painter.drawText(rect, Qt.AlignCenter, "hi")
        painter.restore()

class PastelDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. DEFINE PASTEL COLORS
        pastel_red = QColor("#FFD1D1")
        pastel_blue = QColor("#D1E8FF")
        dark_text = QColor("#2C3E50")  # Soft dark grey for readability

        # 2. LOGIC FOR BACKGROUND
        if option.state & QStyle.State_Selected:
            bg_color = option.palette.highlight().color()
            text_color = Qt.white
        else:
            # Alternating pastel rows
            bg_color = pastel_red if index.row() % 2 == 0 else pastel_blue
            text_color = dark_text

        # 3. DRAW BACKGROUND
        painter.fillRect(option.rect, bg_color)

        # 4. DRAW TEXT
        raw_data = index.data(Qt.DisplayRole) or ""
        key_text, value_text = raw_data.split(":", 1) if ":" in raw_data else ("Item:", raw_data)
        
        rect = option.rect.adjusted(15, 0, 0, 0)
        
        # Draw Key (Lower opacity version of text color)
        painter.setPen(text_color)
        painter.setOpacity(0.7)
        metrics = QFontMetrics(painter.font())
        key_width = metrics.horizontalAdvance(key_text)
        painter.drawText(rect, Qt.AlignVCenter, key_text)

        # Draw Value (Full opacity + Bold)
        painter.setOpacity(1.0)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        
        val_rect = rect.adjusted(key_width + 10, 0, 0, 0)
        painter.drawText(val_rect, Qt.AlignVCenter, value_text)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(0, 45)

def run_app():
    app = QApplication(sys.argv)
    
    # Fusion style is still recommended to ensure the pastels don't get washed out
    app.setStyle("Fusion") 
    
    model = QStandardItemModel(100, 1)
    for i in range(100):
        model.setItem(i, 0, QStandardItem(f"User {i+1:03d}:Active_Session"))

    view = QTableView()
    view.setModel(model)
    
    # UI Cleanup
    view.verticalHeader().hide()
    # view.horizontalHeader().hide()
    view.setHorizontalHeader(CustomHeader(Qt.Horizontal, view))
    view.setShowGrid(False)
    view.setSelectionBehavior(QTableView.SelectRows)
    view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    view.setItemDelegate(PastelDelegate())
    
    view.setWindowTitle("Pastel Alternating Rows")
    view.resize(450, 600)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()