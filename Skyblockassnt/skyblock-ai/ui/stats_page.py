from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt

from ui.widgets.neon_card import NeonCard
from ui.widgets.skill_bar import SkillBar


def compact_coins(value):
    value = float(value)

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:,.0f}"


class StatsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 38, 50, 38)
        layout.setSpacing(20)
        self.setLayout(layout)

        self.profile_header = QLabel("Player Overview")
        self.profile_header.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #46c7ff;
                font-weight: bold;
            }
        """)

        self.profile_name = QLabel("Loading...")
        self.profile_name.setStyleSheet("""
            QLabel {
                font-size: 40px;
                font-weight: 900;
                color: white;
            }
        """)

        self.profile_subtitle = QLabel("")
        self.profile_subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #b4c3d8;
            }
        """)

        layout.addWidget(self.profile_header)
        layout.addWidget(self.profile_name)
        layout.addWidget(self.profile_subtitle)

        # Coin card
        coin_card = NeonCard(minimum_height=160)
        coin_layout = QHBoxLayout()
        coin_layout.setContentsMargins(40, 24, 40, 24)
        coin_card.setLayout(coin_layout)

        self.purse_label = QLabel()
        self.bank_label = QLabel()
        self.total_label = QLabel()

        for label in [
            self.purse_label,
            self.bank_label,
            self.total_label,
        ]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 23px;
                    font-weight: 900;
                    color: white;
                }
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            coin_layout.addWidget(label)

        layout.addWidget(coin_card)

        skills_title = QLabel("📈 Skills")
        skills_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 900;
                color: white;
            }
        """)
        layout.addWidget(skills_title)

        # Skills card
        skills_card = NeonCard(minimum_height=510)
        skills_layout = QVBoxLayout()
        skills_layout.setContentsMargins(28, 24, 28, 24)
        skills_layout.setSpacing(2)
        skills_card.setLayout(skills_layout)

        self.skill_rows = {}

        skills = [
            ("combat", "Combat", 60),
            ("mining", "Mining", 60),
            ("farming", "Farming", 60),
            ("foraging", "Foraging", 60),
            ("fishing", "Fishing", 60),
            ("enchanting", "Enchanting", 60),
            ("alchemy", "Alchemy", 60),
            ("catacombs", "Catacombs", 50),
        ]

        for key, name, max_level in skills:
            row = SkillBar(key, name, max_level)
            skills_layout.addWidget(row)
            self.skill_rows[key] = row

        layout.addWidget(skills_card)

        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setMaximumHeight(90)
        self.details_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(9, 22, 40, 145);
                border: 1px solid rgba(95, 147, 255, 95);
                border-radius: 18px;
                padding: 14px;
                color: #dce8ff;
                font-size: 13px;
            }
        """)

        layout.addWidget(self.details_box)

    def update_stats(self, stats: dict):
        self.profile_name.setText(f"{stats['ign']} 👑")
        self.profile_subtitle.setText(f"Profile: {stats['profile_name']}")

        self.purse_label.setText(
            f"👛\nPurse\n{compact_coins(stats['purse'])}"
        )

        self.bank_label.setText(
            f"🏦\nBank\n{compact_coins(stats['bank'])}"
        )

        self.total_label.setText(
            f"🪙\nTotal\n{compact_coins(stats['total_visible_coins'])}"
        )

        for skill, row in self.skill_rows.items():
            row.set_level(stats.get(skill, 0))

        self.details_box.setText(
            f"Bank Debug: {stats['bank_debug']}\n"
            f"Notes: {stats['notes']}"
        )
