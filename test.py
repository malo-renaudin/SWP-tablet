import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTabletEvent

class TabletTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wacom test")
        self.resize(800, 600)

    def tabletEvent(self, event: QTabletEvent):
        if event.type() == QTabletEvent.TabletMove:
            t = time.time()
            pos = event.pos()
            pressure = event.pressure()
            print(f"{t:.6f}, x={pos.x()}, y={pos.y()}, p={pressure:.3f}")
        event.accept()

app = QApplication(sys.argv)
w = TabletTest()
w.show()
sys.exit(app.exec_())
