import math

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QFont,
    QBrush,
    QPen,
)


class SkillBar(QWidget):
    COLORS = {
        "combat": "#ff4757",
        "mining": "#22c9ff",
        "farming": "#38e05a",
        "foraging": "#12e0b8",
        "fishing": "#16a9ff",
        "enchanting": "#9a66ff",
        "alchemy": "#f25fd5",
        "catacombs": "#ff8a00",
    }

    ICONS = {
        "combat": "⚔️",
        "mining": "⛏️",
        "farming": "🌾",
        "foraging": "🌳",
        "fishing": "🐟",
        "enchanting": "🔮",
        "alchemy": "⚗️",
        "catacombs": "💀",
    }

    def __init__(self, key: str, name: str, max_level: int):
        super().__init__()

        self.key = key
        self.name = name
        self.max_level = max_level
        self.level = 0
        self.hovered = False
        self.phase = 0.0

        self.setMinimumHeight(58)
        self.setMouseTracking(True)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(35)

    def animate(self):
        self.phase += 0.025
        self.update()

    def set_level(self, level):
        self.level = int(level) if isinstance(level, int) else 0
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

        outer = QRectF(4, 5, self.width() - 8, self.height() - 10)

        if self.hovered:
            painter.setBrush(QColor(255, 255, 255, 18))
            painter.setPen(QPen(QColor("#2e86ff"), 1))
            painter.drawRoundedRect(outer, 14, 14)

        painter.setPen(QColor("#eef6ff"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(
            22,
            37,
            f"{self.ICONS.get(self.key, '')}  {self.name}"
        )

        bar_x = 180
        bar_y = 24
        bar_w = max(140, self.width() - 420)
        bar_h = 12

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#10203a"))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 6, 6)

        percent = min(self.level / self.max_level, 1)
        fill_w = max(1, int(bar_w * percent))

        color = QColor(self.COLORS.get(self.key, "#3f7cff"))

        gradient = QLinearGradient(
            bar_x + math.sin(self.phase) * 40,
            bar_y,
            bar_x + fill_w,
            bar_y,
        )

        gradient.setColorAt(0.0, color.lighter(165))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(
            1.0,
            QColor("#ffffff") if self.hovered else color.darker(115)
        )

        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 6, 6)

        painter.setPen(QColor("#b8c7dd"))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(self.width() - 165, 37, "Level")

        painter.setPen(color.lighter(135))
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.drawText(self.width() - 108, 38, str(self.level))

        painter.setPen(QColor("#b8c7dd"))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(self.width() - 70, 37, f"/ {self.max_level}")
