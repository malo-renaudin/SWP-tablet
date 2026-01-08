import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QTabletEvent

class TabletDraw(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wacom drawing test")
        self.resize(800, 600)

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.last_pos = None

    def tabletEvent(self, event: QTabletEvent):
        if event.type() == QTabletEvent.TabletPress:
            self.last_pos = event.pos()

        elif event.type() == QTabletEvent.TabletMove and self.last_pos is not None:
            pos = event.pos()
            pressure = event.pressure()

            # Timestamp for logging later
            t = time.time()

            # Draw
            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.Antialiasing, True)

            pen = QPen(QColor(0, 0, 0))
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            pen.setWidthF(1.5 + pressure * 6)

            painter.setPen(pen)
            painter.drawLine(self.last_pos, pos)
            painter.end()


            print(f"{t:.6f}, x={pos.x()}, y={pos.y()}, p={pressure:.3f}")

            self.last_pos = pos
            self.update()

        elif event.type() == QTabletEvent.TabletRelease:
            self.last_pos = None

        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

app = QApplication(sys.argv)
w = TabletDraw()
w.show()
sys.exit(app.exec_())
