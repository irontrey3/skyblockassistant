import math

from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QPen,
    QBrush,
)


class NeonCard(QFrame):
    def __init__(self, minimum_height=150):
        super().__init__()

        self.t = 0.0
        self.hovered = False

        self.setMinimumHeight(minimum_height)
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(28)

    def animate(self):
        self.t += 0.012
        self.update()

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(
            8,
            8,
            self.width() - 16,
            self.height() - 16
        )

        # frosted glass body
        glass = QLinearGradient(rect.topLeft(), rect.bottomRight())
        glass.setColorAt(0.0, QColor(35, 55, 90, 155))
        glass.setColorAt(0.45, QColor(8, 22, 40, 175))
        glass.setColorAt(1.0, QColor(10, 55, 48, 135))

        painter.setBrush(QBrush(glass))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 26, 26)

        # soft inner shine
        shine = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        shine.setColorAt(0.0, QColor(255, 255, 255, 36))
        shine.setColorAt(0.35, QColor(255, 255, 255, 9))
        shine.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setBrush(QBrush(shine))
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 24, 24)

        # animated glowing border
        glow_alpha = 145 if self.hovered else 90

        x1 = rect.left() + math.sin(self.t) * rect.width()
        y1 = rect.top() + math.cos(self.t * 0.8) * rect.height()
        x2 = rect.right() + math.cos(self.t * 1.2) * rect.width()
        y2 = rect.bottom() + math.sin(self.t * 0.9) * rect.height()

        border = QLinearGradient(x1, y1, x2, y2)

        c1 = QColor("#14b8ff")
        c1.setAlpha(glow_alpha)

        c2 = QColor("#8b5cff")
        c2.setAlpha(glow_alpha)

        c3 = QColor("#42ff7b")
        c3.setAlpha(glow_alpha)

        border.setColorAt(0.0, c1)
        border.setColorAt(0.5, c2)
        border.setColorAt(1.0, c3)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QBrush(border), 3 if self.hovered else 2))
        painter.drawRoundedRect(rect, 26, 26)
