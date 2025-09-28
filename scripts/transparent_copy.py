import sys
from PyQt5.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PyQt5.QtGui import QClipboard, QImage, QColor, QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Transparent Clipboard Example")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Example PNG with transparency", self)
        layout.addWidget(self.label)
        
        # Create a transparent QImage
        self.transparent_image = self.create_transparent_image(200, 200)
        self.label.setPixmap(QPixmap.fromImage(self.transparent_image))

        self.copy_button = QPushButton("Copy Transparent Image to Clipboard")
        self.copy_button.clicked.connect(self.copy_image_to_clipboard)
        layout.addWidget(self.copy_button)

    def create_transparent_image(self, width, height):
        # Create an image with an alpha channel
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))  # Fill with transparent color

        # Draw on the image
        painter = QPainter(image)
        painter.setBrush(QColor(255, 0, 0, 128))  # Semi-transparent red brush
        painter.drawEllipse(20, 20, 160, 160)
        painter.end()
        return image

    def copy_image_to_clipboard(self):
        clipboard = QApplication.clipboard()
        
        # Method 1: Use QMimeData with PNG data (best for compatible apps)
        mime_data = self.transparent_image_to_mimedata(self.transparent_image)
        clipboard.setMimeData(mime_data)

        # Method 2 (Fallback): Use QClipboard.setImage()
        # This will work in more apps but will likely lose transparency.
        # clipboard.setImage(self.transparent_image)

        print("Transparent image (with PNG data) copied to clipboard.")

    def transparent_image_to_mimedata(self, image):
        # Create a QByteArray and QBuffer to hold the PNG data
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        buffer.close()

        # Create QMimeData and set the image/png format
        mime_data = self.transparent_image.mimeData()
        mime_data.setData("image/png", byte_array)
        
        return mime_data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
