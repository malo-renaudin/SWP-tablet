import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QTabletEvent

class TabletFade(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wacom fade test")
        self.resize(800, 600)

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.last_pos = None

        # Fading timer
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.fade)
        self.fade_timer.start(100)  # ms between fading steps

    def fade(self):
        painter = QPainter(self.image)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 20))  # 20 = alpha
        painter.end()
        self.update()

    def tabletEvent(self, event: QTabletEvent):
        if event.type() == QTabletEvent.TabletPress:
            self.last_pos = event.pos()

        elif event.type() == QTabletEvent.TabletMove and self.last_pos is not None:
            pos = event.pos()
            pressure = event.pressure()
            t = time.time()
            print(f"{t:.6f}, x={pos.x()}, y={pos.y()}, p={pressure:.3f}")

            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen = QPen(Qt.black)
            pen.setWidthF(1 + pressure * 6)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_pos, pos)
            painter.end()

            self.last_pos = pos
            self.update()

        elif event.type() == QTabletEvent.TabletRelease:
            self.last_pos = None

        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

app = QApplication(sys.argv)
w = TabletFade()
w.show()
sys.exit(app.exec_())
