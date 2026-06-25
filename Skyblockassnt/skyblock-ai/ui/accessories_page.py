from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from engines.accessories_engine import (
    get_missing_accessories,
    get_owned_accessories,
    calculate_magical_power,
    extract_owned_accessory_ids,
    search_accessories,
    accessories_to_table_rows
)

class SortableTableItem(QTableWidgetItem):
    def __lt__(self, other):
        left = self.data(Qt.ItemDataRole.UserRole)
        right = other.data(Qt.ItemDataRole.UserRole)

        try:
            return left < right
        except Exception:
            return self.text() < other.text()

class AccessoriesPage(QWidget):
    def __init__(self):
        super().__init__()

        self.profile_data = None
        self.current_items = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Accessories & Magical Power")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Track owned accessories, missing accessories, and MP gains.")
        subtitle.setObjectName("PageSubtitle")

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        self.mp_card = self.make_stat_card("Magical Power", "0")
        self.owned_card = self.make_stat_card("Owned", "0")
        self.missing_card = self.make_stat_card("Missing", "0")

        stats_row.addWidget(self.mp_card)
        stats_row.addWidget(self.owned_card)
        stats_row.addWidget(self.missing_card)

        controls = QHBoxLayout()
        controls.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search accessories...")
        self.search_input.textChanged.connect(self.search_items)

        self.missing_button = QPushButton("Missing")
        self.missing_button.clicked.connect(self.show_missing)

        self.owned_button = QPushButton("Owned")
        self.owned_button.clicked.connect(self.show_owned)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_search)

        controls.addWidget(self.search_input, 1)
        controls.addWidget(self.missing_button)
        controls.addWidget(self.owned_button)
        controls.addWidget(self.clear_button)

        self.status_label = QLabel("Waiting for profile data...")
        self.status_label.setObjectName("StatusLabel")

        card = QFrame()
        card.setObjectName("GlassCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Rarity", "MP", "Price", "Coins/MP", "Source", "Priority"
        ])

        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        card_layout.addWidget(self.table)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(stats_row)
        layout.addLayout(controls)
        layout.addWidget(self.status_label)
        layout.addWidget(card, 1)

        self.setStyleSheet("""
            QLabel#PageTitle {
                font-size: 34px;
                font-weight: 900;
                color: white;
            }

            QLabel#PageSubtitle,
            QLabel#StatusLabel {
                color: rgba(255, 255, 255, 0.65);
                font-size: 14px;
            }

            QFrame#GlassCard,
            QFrame#StatCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 22px;
            }

            QLabel#StatTitle {
                color: rgba(255, 255, 255, 0.65);
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#StatValue {
                color: white;
                font-size: 28px;
                font-weight: 900;
            }

            QLineEdit {
                background: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 15px;
                padding: 12px 16px;
                color: white;
                font-size: 14px;
            }

            QLineEdit:focus {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(120, 180, 255, 0.9);
            }

            QPushButton {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 15px;
                padding: 12px 18px;
                color: white;
                font-weight: 800;
            }

            QPushButton:hover {
                background: rgba(120, 180, 255, 0.28);
                border: 1px solid rgba(120, 180, 255, 0.8);
            }

            QTableWidget {
                background: transparent;
                border: none;
                color: white;
                font-size: 13px;
                alternate-background-color: rgba(255, 255, 255, 0.04);
            }

            QHeaderView::section {
                background: rgba(255, 255, 255, 0.13);
                color: white;
                border: none;
                padding: 10px;
                font-weight: 900;
            }

            QTableWidget::item:selected {
                background: rgba(120, 180, 255, 0.35);
            }
        """)

    def make_stat_card(self, title, value):
        card = QFrame()
        card.setObjectName("StatCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        title_label = QLabel(title)
        title_label.setObjectName("StatTitle")

        value_label = QLabel(value)
        value_label.setObjectName("StatValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    def set_profile_data(self, profile_data):
        self.profile_data = profile_data

        if not self.profile_data:
            self.status_label.setText("No profile data loaded.")
            self.table.setRowCount(0)
            return

        self.update_stats()
        self.show_missing()

    def update_stats(self):
        mp = self.profile_data.get("magical_power", 0)
        owned_count = self.profile_data.get("accessories_count", 0)

        owned = get_owned_accessories(self.profile_data)
        missing = get_missing_accessories(self.profile_data)

        if owned_count == 0:
         owned_count = len(owned)

        self.mp_card.value_label.setText(str(mp))
        self.owned_card.value_label.setText(str(owned_count))
        self.missing_card.value_label.setText(str(len(missing)))

    def show_missing(self):
        if not self.profile_data:
            self.status_label.setText("No profile data loaded.")
            return

        items = get_missing_accessories(self.profile_data)
        self.current_items = items
        self.populate_table(items)
        self.status_label.setText(f"Showing {len(items)} missing accessories.")

    def show_owned(self):
        if not self.profile_data:
            self.status_label.setText("No profile data loaded.")
            return

        items = get_owned_accessories(self.profile_data)
        self.current_items = items
        self.populate_table(items)
        self.status_label.setText(f"Showing {len(items)} owned accessories.")

    def search_items(self):
        query = self.search_input.text()

        if not self.current_items:
            return

        results = search_accessories(self.current_items, query)
        self.populate_table(results)

        if query.strip():
            self.status_label.setText(f"Showing {len(results)} results for '{query}'.")
        else:
            self.status_label.setText(f"Showing {len(results)} accessories.")

    def clear_search(self):
        self.search_input.clear()
        self.show_missing()

    def populate_table(self, items):
        rows = accessories_to_table_rows(items)

        columns = [
            "Name", "Rarity", "MP", "Price", "Coins/MP", "Source", "Priority"
        ]

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            accessory = items[row_index]

            for col_index, column in enumerate(columns):
                value = row.get(column, "")
                cell = SortableTableItem(str(value))

                # Store raw numeric values for proper sorting
                if column == "MP":
                    cell.setData(Qt.ItemDataRole.UserRole, int(accessory.get("mp", 0)))

                elif column == "Price":
                    price = accessory.get("estimated_price")

                    if isinstance(price, str):
                        try:
                            price = int(float(price.replace(",", "").strip()))
                        except (ValueError, TypeError):
                            price = None

                    if price is None:
                        price = 999999999999

                    cell.setData(Qt.ItemDataRole.UserRole, int(price))

                elif column == "Coins/MP":
                    price = accessory.get("estimated_price")
                    mp = accessory.get("mp", 0)

                    if isinstance(price, str):
                        try:
                            price = int(float(price.replace(",", "").strip()))
                        except (ValueError, TypeError):
                            price = None

                    try:
                        mp = int(mp)
                    except (TypeError, ValueError):
                        mp = 0

                    if price is None or mp <= 0:
                        coins_per_mp = 999999999999
                    else:
                        coins_per_mp = int(price / mp)

                    cell.setData(Qt.ItemDataRole.UserRole, coins_per_mp)

                elif column == "Priority":
                    cell.setData(Qt.ItemDataRole.UserRole, int(accessory.get("priority", 0)))

                else:
                    cell.setData(Qt.ItemDataRole.UserRole, str(value).lower())

                if col_index == 0 or column == "Source":
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                else:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if column == "Rarity":
                    self.color_rarity_cell(cell, value)

                elif column == "MP":
                    cell.setForeground(QColor("#66ccff"))

                elif column == "Price":
                    cell.setForeground(QColor("#ffaa00"))

                elif column == "Coins/MP":
                    cell.setForeground(QColor("#00ff88"))

                elif column == "Priority":
                    cell.setForeground(QColor("#ffd700"))

                self.table.setItem(row_index, col_index, cell)

        self.table.setSortingEnabled(True)

    def color_rarity_cell(self, cell, rarity):
        colors = {
            "COMMON": "#ffffff",
            "UNCOMMON": "#55ff55",
            "RARE": "#5555ff",
            "EPIC": "#aa00aa",
            "LEGENDARY": "#ffaa00",
            "MYTHIC": "#ff55ff",
            "SPECIAL": "#ff5555",
            "VERY_SPECIAL": "#ff5555",
        }

        cell.setForeground(QColor(colors.get(rarity, "#ffffff")))