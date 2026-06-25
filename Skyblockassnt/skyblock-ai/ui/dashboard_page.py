from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

from ui.widgets.neon_card import NeonCard


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 38, 50, 38)
        layout.setSpacing(22)
        self.setLayout(layout)

        title = QLabel("📊 Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 40px;
                font-weight: 900;
                color: white;
            }
        """)

        subtitle = QLabel("Your live SkyBlock profile overview")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #b4c3d8;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.summary_card = NeonCard(minimum_height=230)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(35, 26, 35, 26)
        self.summary_card.setLayout(card_layout)

        self.summary_text = QLabel("Loading...")
        self.summary_text.setStyleSheet("""
            QLabel {
                font-size: 19px;
                font-weight: 700;
                color: white;
            }
        """)

        card_layout.addWidget(self.summary_text)
        layout.addWidget(self.summary_card)

        self.recommendation_box = QTextEdit()
        self.recommendation_box.setReadOnly(True)
        self.recommendation_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(9, 22, 40, 145);
                border: 1px solid rgba(95, 147, 255, 95);
                border-radius: 18px;
                padding: 16px;
                color: #dce8ff;
                font-size: 14px;
            }
        """)

        layout.addWidget(self.recommendation_box)

    def update_dashboard(self, ign: str, uuid: str, stats: dict, profile_count: int, bazaar_ok: bool):
        self.summary_text.setText(
            f"👤 IGN: {ign}\n"
            f"🧬 UUID: {uuid}\n"
            f"🍀 Profile: {stats['profile_name']}\n\n"
            f"⚔️ Combat: {stats['combat']}\n"
            f"⛏️ Mining: {stats['mining']}\n"
            f"🎣 Fishing: {stats['fishing']}\n"
            f"💀 Catacombs: {stats['catacombs']}\n\n"
            f"💰 Total Visible Coins: {stats['total_visible_coins']:,}"
        )

        self.recommendation_box.setText(
            f"✅ API Loaded\n\n"
            f"Profiles Found: {profile_count}\n"
            f"Bazaar Loaded: {bazaar_ok}\n\n"
            f"Next build step:\n"
            f"- Add Bazaar page integration\n"
            f"- Add AH engine\n"
            f"- Add MP optimizer\n"
            f"- Add AI advisor"
        )
