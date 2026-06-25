import math

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QRadialGradient


class AnimatedBackground(QWidget):
    def __init__(self):
        super().__init__()

        self.t = 0.0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.t += 0.012
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor("#020814"))

        blobs = [
            ("#216dff", 0.20, 0.25, 280, 1.0),
            ("#8b5cff", 0.78, 0.18, 330, 1.5),
            ("#00f0b5", 0.62, 0.78, 350, 2.0),
            ("#14b8ff", 0.25, 0.86, 280, 2.8),
        ]

        for color, base_x, base_y, radius, speed in blobs:
            x = self.width() * base_x + math.sin(self.t * speed) * 60
            y = self.height() * base_y + math.cos(self.t * speed * 0.8) * 50

            gradient = QRadialGradient(x, y, radius)

            center = QColor(color)
            center.setAlpha(95)

            middle = QColor(color)
            middle.setAlpha(22)

            edge = QColor(color)
            edge.setAlpha(0)

            gradient.setColorAt(0.0, center)
            gradient.setColorAt(0.45, middle)
            gradient.setColorAt(1.0, edge)

            painter.setBrush(QBrush(gradient))
            painter.setPen(QColor(0, 0, 0, 0))
            painter.drawEllipse(
                QRectF(
                    x - radius,
                    y - radius,
                    radius * 2,
                    radius * 2,
                )
            )
