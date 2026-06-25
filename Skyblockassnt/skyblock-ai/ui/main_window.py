import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QStackedWidget,
)

from api.hypixel_api import load_config, get_skyblock_profiles, get_bazaar
from api.mojang_api import get_uuid
from engines.profile_engine import parse_profile_stats

from ui.widgets.animated_background import AnimatedBackground
from ui.widgets.glow_button import GlowButton

from ui.dashboard_page import DashboardPage
from ui.stats_page import StatsPage
from ui.api_page import ApiPage
from ui.bazaar_page import BazaarPage
from ui.accessories_page import AccessoriesPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SkyBlock AI V4")
        self.setGeometry(80, 80, 1550, 920)

        self.setStyleSheet("""
            QWidget {
                color: #edf4ff;
                font-family: Segoe UI;
            }

            QTextEdit {
                background-color: rgba(9, 22, 40, 145);
                border: 1px solid rgba(95, 147, 255, 95);
                border-radius: 18px;
                padding: 14px;
                color: #dce8ff;
                font-size: 13px;
            }

            QLineEdit {
                background-color: rgba(9, 22, 40, 145);
                border: 1px solid rgba(95, 147, 255, 95);
                border-radius: 14px;
                padding: 12px;
                color: white;
            }
        """)

        self.background = AnimatedBackground()
        self.setCentralWidget(self.background)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.background.setLayout(self.main_layout)

        self.build_sidebar()
        self.build_pages()

        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.pages)

        self.switch_page(0)
        self.refresh_api()

    def build_sidebar(self):
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(22, 32, 22, 22)
        sidebar.setSpacing(14)

        logo = QLabel("🧊\nSkyBlock AI")
        logo.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-weight: 900;
                color: white;
                padding: 18px;
            }
        """)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sidebar.addWidget(logo)

        self.dashboard_button = GlowButton("▦   Dashboard")
        self.stats_button = GlowButton("👤   Stats")
        self.bazaar_button = GlowButton("💰   Bazaar")
        self.accessories_button = GlowButton("💎   Accessories")
        self.api_button = GlowButton("⚗   API Debug")
        self.refresh_button = GlowButton("⟳   Refresh")

        self.nav_buttons = [
            self.dashboard_button,
            self.stats_button,
            self.bazaar_button,
            self.accessories_button,
            self.api_button,
        ]

        for button in [
            self.dashboard_button,
            self.stats_button,
            self.bazaar_button,
            self.accessories_button,
            self.api_button,
            self.refresh_button,
        ]:
            sidebar.addWidget(button)

        sidebar.addStretch()

        self.status_label = QLabel("🟢 API Status\nReady")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(9, 22, 40, 125);
                border: 1px solid rgba(95, 147, 255, 90);
                border-radius: 20px;
                padding: 18px;
                color: #c8d7ee;
                font-size: 14px;
            }
        """)

        sidebar.addWidget(self.status_label)

        self.sidebar_widget = QFrame()
        self.sidebar_widget.setLayout(sidebar)
        self.sidebar_widget.setFixedWidth(275)
        self.sidebar_widget.setStyleSheet("""
            QFrame {
                background-color: rgba(4, 15, 28, 150);
                border-right: 1px solid rgba(95, 147, 255, 70);
            }
        """)

        self.dashboard_button.clicked.connect(lambda: self.switch_page(0))
        self.stats_button.clicked.connect(lambda: self.switch_page(1))
        self.bazaar_button.clicked.connect(lambda: self.switch_page(2))
        self.accessories_button.clicked.connect(lambda: self.switch_page(3))
        self.api_button.clicked.connect(lambda: self.switch_page(4))
        self.refresh_button.clicked.connect(self.refresh_api)

    def build_pages(self):
        self.pages = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.stats_page = StatsPage()
        self.bazaar_page = BazaarPage()
        self.accessories_page = AccessoriesPage()
        self.api_page = ApiPage()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.stats_page)
        self.pages.addWidget(self.bazaar_page)
        self.pages.addWidget(self.accessories_page)
        self.pages.addWidget(self.api_page)

    def switch_page(self, index: int):
        self.pages.setCurrentIndex(index)

        for i, button in enumerate(self.nav_buttons):
            button.set_selected(i == index)

    def refresh_api(self):
        try:
            config = load_config()
            ign = config["ign"]

            uuid_data = get_uuid(ign)
            uuid = uuid_data["json"].get("id")

            if uuid is None:
                raise Exception("Could not get UUID. Check config.json IGN.")

            profile_data = get_skyblock_profiles(uuid)
            bazaar_data = get_bazaar()

            stats = parse_profile_stats(profile_data, uuid, ign)
            print("\nACCESSORY DEBUG:")
            print(stats)
            print

            profiles = profile_data.get("json", {}).get("profiles", [])

            selected_profile = None
            
            for profile in profiles:
                if profile.get("selected"):
                    selected_profile = profile
                    break
            if selected_profile is None and profiles:
                selected_profile = profiles[0]

            member = selected_profile.get("members", {}).get(uuid, {}) if selected_profile else {}

            print("\nSELECTED PROFILE DEBUG:")
            print(selected_profile.get("cute_name") if selected_profile else "None")
            print()

            print("\nMEMBERS KEYS DEBUG:")
            print(member.keys())
            print()

            print("\nACCESSORY BAG DEBUG:")
            print(member.get("accessory_bag_storage", {}))
            print()

            print("\nINVENTORY DEBUG:")
            print(member.get("inventory", {}).keys())
            print()

            print("\nBAG CONTENTS DEBUG:")
            bag_contents = member.get("inventory", {}).get("bag_contents", {})
            print(type(bag_contents))
            print(bag_contents.keys() if isinstance(bag_contents, dict) else bag_contents)
            print()

            print("\nTALISMAN BAG DEBUG:")
            talisman_bag = (
                member
                .get("inventory", {})
                .get("bag_contents", {})
                .get("talisman_bag", {})
            )
            print(type(talisman_bag))
            print(talisman_bag)
            print()

            print("\nITEM DATA DEBUG:")
            print(member.get("item_data", {}).keys())
            print()

            print("\nSHARED INVENTORY DEBUG:")
            print(member.get("shared_inventory", {}).keys())
            print()

            profile_count = len(profile_data["json"].get("profiles", []))
            bazaar_ok = bazaar_data.get("ok", False)

            self.dashboard_page.update_dashboard(
                ign=ign,
                uuid=uuid,
                stats=stats,
                profile_count=profile_count,
                bazaar_ok=bazaar_ok,
            )

            self.stats_page.update_stats(stats)
            self.bazaar_page.set_bazaar_data(bazaar_data)

            # Accessories page currently uses profile_data.
            # Later we can make the engine parse the exact selected SkyBlock profile.
            self.accessories_page.set_profile_data(stats)

            debug_output = {
                "mojang_call": uuid_data,
                "profiles_call": profile_data,
                "bazaar_call": bazaar_data,
                "parsed_stats": stats,
            }

            self.api_page.set_debug_data(debug_output)

            self.status_label.setText("🟢 API Status\nLoaded successfully")

        except Exception as error:
            message = str(error)

            self.status_label.setText("🔴 API Status\nError")

            try:
                self.api_page.set_error(message)
            except Exception:
                print(message)
