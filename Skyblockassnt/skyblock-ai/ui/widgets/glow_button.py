from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QPen,
    QFont,
    QBrush,
)


class GlowButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)

        self.selected = False
        self.hovered = False

        self.setMinimumHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QPushButton{
                background: transparent;
                border: none;
            }
        """)

    def set_selected(self, value: bool):
        self.selected = value
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
            4,
            4,
            self.width() - 8,
            self.height() - 8
        )

        if self.selected or self.hovered:

            alpha = 220 if self.selected else 110

            gradient = QLinearGradient(
                rect.left(),
                rect.top(),
                rect.right(),
                rect.bottom()
            )

            c1 = QColor("#14b8ff")
            c1.setAlpha(alpha)

            c2 = QColor("#8b5cff")
            c2.setAlpha(alpha)

            gradient.setColorAt(0, c1)
            gradient.setColorAt(1, c2)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 16, 16)

        if self.selected:
            border = QPen(QColor("#7df9ff"), 2)
            painter.setPen(border)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, 16, 16)

        painter.setPen(
            QColor("#ffffff")
            if (self.selected or self.hovered)
            else QColor("#b8c7dd")
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Weight.Bold
                if self.selected
                else QFont.Weight.Normal
            )
        )

        painter.drawText(
            rect.adjusted(18, 0, 0, 0),
            Qt.AlignmentFlag.AlignVCenter,
            self.text()
        )
