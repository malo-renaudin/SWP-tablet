import sys
import time
import csv
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QTabletEvent, QPainterPath

class WacomTracker(QWidget):
    def __init__(self, udp_port=5005, fade_interval=30, fade_alpha=20):
        super().__init__()
        self.setWindowTitle("Wacom Tracker")
        self.resize(800, 600)

        # Canvas
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        # Tablet state
        self.last_pos = None
        self.points = []

        # Fading effect
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.fade)
        self.fade_timer.start(fade_interval)
        self.fade_alpha = fade_alpha

        # Data storage
        self.data = []

        # UDP triggers
        self.udp_port = udp_port
        self.udp_thread = threading.Thread(target=self.listen_udp, daemon=True)
        self.udp_thread.start()

    # -------------------- UDP Trigger Listener --------------------
    def listen_udp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.udp_port))
        print(f"Listening for UDP triggers on port {self.udp_port}...")
        while True:
            data, addr = sock.recvfrom(1024)
            t = time.time()
            try:
                # Try to read as byte first
                if len(data) == 1:
                    trigger = int(data[0])
                else:
                    trigger = int(data.decode())
            except ValueError:
                trigger = data.decode()
            print(f"Trigger received: {trigger} at {t:.6f}")

            self.data.append({
                "timestamp": t,
                "x": None,
                "y": None,
                "pressure": None,
                "event": f"trigger_{trigger}"
            })

    # -------------------- Fading --------------------
    def fade(self):
        painter = QPainter(self.image)
        painter.fillRect(self.rect(), QColor(255, 255, 255, self.fade_alpha))
        painter.end()
        self.update()

    # -------------------- Tablet Events --------------------
    def tabletEvent(self, event: QTabletEvent):
        t = time.time()
        pos = event.pos()
        pressure = event.pressure()

        if event.type() == QTabletEvent.TabletPress:
            self.last_pos = pos
            self.points = [pos]
            self.data.append({"timestamp": t, "x": pos.x(), "y": pos.y(), "pressure": pressure, "event": "press"})

        elif event.type() == QTabletEvent.TabletMove and self.last_pos is not None:
            self.points.append(pos)
            self.data.append({"timestamp": t, "x": pos.x(), "y": pos.y(), "pressure": pressure, "event": "move"})

            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen = QPen(Qt.black)
            pen.setWidthF(1 + pressure * 6)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)

            # Bézier smoothing using last 3 points
            if len(self.points) >= 3:
                p1 = self.points[-3]
                p2 = self.points[-2]
                p3 = self.points[-1]
                path = QPainterPath(p1)
                mid = QPoint((p2.x() + p3.x()) // 2, (p2.y() + p3.y()) // 2)
                path.quadTo(p2, mid)
                painter.drawPath(path)
            else:
                painter.drawLine(self.last_pos, pos)

            painter.end()
            self.last_pos = pos
            self.update()

        elif event.type() == QTabletEvent.TabletRelease:
            self.data.append({"timestamp": t, "x": pos.x(), "y": pos.y(), "pressure": pressure, "event": "release"})
            self.last_pos = None
            self.points = []

        event.accept()

    # -------------------- Paint --------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    # -------------------- Save CSV --------------------
    def save_csv(self, filename="tablet_log.csv"):
        keys = ["timestamp", "x", "y", "pressure", "event"]
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.data)
        print(f"Saved {len(self.data)} events to {filename}")

# -------------------- Main --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WacomTracker()
    w.show()

    try:
        sys.exit(app.exec_())
    finally:
        w.save_csv()  # Automatically save at the end
