import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from engines.bazaar_engine import (
    get_top_flips,
    search_bazaar,
    bazaar_items_to_table_rows
)


FAVORITES_FILE = "bazaar_favorites.json"

class SortableTableItem(QTableWidgetItem):
    def __lt__(self, other):
        left = self.data(Qt.ItemDataRole.UserRole)
        right = other.data(Qt.ItemDataRole.UserRole)

        try:
            return left < right
        except Exception:
            return self.text() < other.text()

class BazaarPage(QWidget):
    def __init__(self):
        super().__init__()

        self.bazaar_data = None
        self.current_items = []
        self.favorites = self.load_favorites()

        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.auto_refresh_tick)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        left = QVBoxLayout()
        left.setSpacing(14)

        title = QLabel("Bazaar Market")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Flips, score, liquidity, risk, favorites, and live refresh.")
        subtitle.setObjectName("PageSubtitle")

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Bazaar items...")
        self.search_input.textChanged.connect(self.search_items)

        self.top_flips_button = QPushButton("Top Flips")
        self.top_flips_button.clicked.connect(self.show_top_flips)

        self.elite_button = QPushButton("Elite")
        self.elite_button.clicked.connect(self.show_elite)

        self.stable_button = QPushButton("Stable")
        self.stable_button.clicked.connect(self.show_stable)

        self.high_volume_button = QPushButton("High Volume")
        self.high_volume_button.clicked.connect(self.show_high_volume)

        controls.addWidget(self.search_input, 1)
        controls.addWidget(self.top_flips_button)
        controls.addWidget(self.elite_button)
        controls.addWidget(self.stable_button)
        controls.addWidget(self.high_volume_button)

        second_controls = QHBoxLayout()
        second_controls.setSpacing(10)

        self.favorite_button = QPushButton("⭐ Favorite Selected")
        self.favorite_button.clicked.connect(self.toggle_selected_favorite)

        self.show_favorites_button = QPushButton("Show Favorites")
        self.show_favorites_button.clicked.connect(self.show_favorites)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_search)

        self.auto_refresh_box = QCheckBox("Auto Refresh")
        self.auto_refresh_box.stateChanged.connect(self.toggle_auto_refresh)

        second_controls.addWidget(self.favorite_button)
        second_controls.addWidget(self.show_favorites_button)
        second_controls.addWidget(self.clear_button)
        second_controls.addWidget(self.auto_refresh_box)

        self.status_label = QLabel("Waiting for Bazaar data...")
        self.status_label.setObjectName("StatusLabel")

        card = QFrame()
        card.setObjectName("GlassCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "★", "Item", "Buy Price", "Sell Price", "Profit", "Profit %",
            "Liquidity", "Score", "Tier", "Risk"
        ])

        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.update_details_panel)

        card_layout.addWidget(self.table)

        left.addWidget(title)
        left.addWidget(subtitle)
        left.addLayout(controls)
        left.addLayout(second_controls)
        left.addWidget(self.status_label)
        left.addWidget(card, 1)

        self.details = QFrame()
        self.details.setObjectName("DetailsPanel")
        details_layout = QVBoxLayout(self.details)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(12)

        self.details_title = QLabel("Select an Item")
        self.details_title.setObjectName("DetailsTitle")

        self.details_body = QLabel("Click a Bazaar item to view details.")
        self.details_body.setObjectName("DetailsBody")
        self.details_body.setWordWrap(True)

        details_layout.addWidget(self.details_title)
        details_layout.addWidget(self.details_body)
        details_layout.addStretch()

        main_layout.addLayout(left, 4)
        main_layout.addWidget(self.details, 1)

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
            QFrame#DetailsPanel {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 22px;
            }

            QLabel#DetailsTitle {
                color: white;
                font-size: 22px;
                font-weight: 900;
            }

            QLabel#DetailsBody {
                color: rgba(255, 255, 255, 0.75);
                font-size: 14px;
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

            QPushButton, QCheckBox {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 15px;
                padding: 11px 16px;
                color: white;
                font-weight: 800;
            }

            QPushButton:hover, QCheckBox:hover {
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

    def get_all_items(self):
        if not self.bazaar_data:
            return []

        return search_bazaar(self.bazaar_data, "", limit=5000)

    def load_favorites(self):
        if not os.path.exists(FAVORITES_FILE):
            return set()

        try:
            with open(FAVORITES_FILE, "r") as file:
                return set(json.load(file))
        except Exception:
            return set()

    def save_favorites(self):
        with open(FAVORITES_FILE, "w") as file:
            json.dump(list(self.favorites), file, indent=2)

    def set_bazaar_data(self, bazaar_data):
        self.bazaar_data = bazaar_data

        if not self.bazaar_data:
            self.status_label.setText("No Bazaar data loaded.")
            self.table.setRowCount(0)
            return

        self.show_top_flips()

    def show_top_flips(self):
        if not self.bazaar_data:
            self.status_label.setText("No Bazaar data loaded.")
            return

        items = get_top_flips(self.bazaar_data, limit=75)
        self.populate_table(items)
        self.status_label.setText(f"Showing {len(items)} top flips.")

    def search_items(self):
        if not self.bazaar_data:
            return

        query = self.search_input.text()
        items = search_bazaar(self.bazaar_data, query, limit=150)
        self.populate_table(items)

        if query.strip():
            self.status_label.setText(f"Showing {len(items)} results for '{query}'.")
        else:
            self.status_label.setText(f"Showing {len(items)} Bazaar items.")

    def show_elite(self):
        items = self.get_all_items()
        items = [
            item for item in items
            if item.get("tier") == "ELITE" and item.get("spread", 0) > 0
        ]
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.populate_table(items[:100])
        self.status_label.setText(f"Showing {len(items[:100])} elite flips.")

    def show_stable(self):
        items = self.get_all_items()
        items = [
            item for item in items
            if item.get("risk") == "Stable" and item.get("spread", 0) > 0
        ]
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.populate_table(items[:100])
        self.status_label.setText(f"Showing {len(items[:100])} stable items.")

    def show_high_volume(self):
        items = self.get_all_items()
        items = [
            item for item in items
            if item.get("spread", 0) > 0
        ]
        items.sort(key=lambda x: x.get("liquidity", 0), reverse=True)
        self.populate_table(items[:100])
        self.status_label.setText("Showing high volume flips.")

    def show_favorites(self):
        items = self.get_all_items()
        items = [
            item for item in items
            if item.get("product_id") in self.favorites
        ]
        self.populate_table(items)
        self.status_label.setText(f"Showing {len(items)} favorites.")

    def clear_search(self):
        self.search_input.clear()
        self.show_top_flips()

    def toggle_auto_refresh(self):
        if self.auto_refresh_box.isChecked():
            self.auto_timer.start(10000)
            self.status_label.setText("Auto refresh enabled.")
        else:
            self.auto_timer.stop()
            self.status_label.setText("Auto refresh disabled.")

    def auto_refresh_tick(self):
        now = datetime.now().strftime("%I:%M:%S %p")
        self.show_top_flips()
        self.status_label.setText(f"Auto refreshed at {now}.")

    def get_selected_product_id(self):
        row = self.table.currentRow()

        if row < 0:
            return None

        item_cell = self.table.item(row, 1)

        if item_cell is None:
            return None

        return item_cell.data(Qt.ItemDataRole.UserRole)

    def toggle_selected_favorite(self):
        product_id = self.get_selected_product_id()

        if not product_id:
            self.status_label.setText("Select an item first.")
            return

        if product_id in self.favorites:
            self.favorites.remove(product_id)
            self.status_label.setText("Removed from favorites.")
        else:
            self.favorites.add(product_id)
            self.status_label.setText("Added to favorites.")

        self.save_favorites()
        self.populate_table(self.current_items)

    def update_details_panel(self):
        product_id = self.get_selected_product_id()

        if not product_id:
            return

        item = None
        for current_item in self.current_items:
            if current_item.get("product_id") == product_id:
                item = current_item
                break

        if item is None:
            return

        self.details_title.setText(item.get("name", "Unknown Item"))
        self.details_body.setText(
            f"ID: {item.get('product_id', 'UNKNOWN')}\n\n"
            f"Buy Price: {item.get('buy_price', 0):,.1f}\n"
            f"Sell Price: {item.get('sell_price', 0):,.1f}\n\n"
            f"Profit: {item.get('spread', 0):,.1f}\n"
            f"Profit %: {item.get('spread_percent', 0):.2f}%\n\n"
            f"Buy Volume: {item.get('buy_volume', 0):,.0f}\n"
            f"Sell Volume: {item.get('sell_volume', 0):,.0f}\n"
            f"Liquidity: {item.get('liquidity', 0):,.0f}\n\n"
            f"Score: {item.get('score', 0):,.0f}\n"
            f"Tier: {item.get('tier', 'NONE')}\n"
            f"Risk: {item.get('risk', 'Unknown')}"
        )

    def populate_table(self, items):
        self.current_items = items
        rows = bazaar_items_to_table_rows(items)

        columns = [
            "★", "Item", "Buy Price", "Sell Price", "Profit", "Profit %",
            "Liquidity", "Score", "Tier", "Risk"
        ]

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            item = items[row_index]
            product_id = item.get("product_id", "")
            is_fav = product_id in self.favorites

            for col_index, column in enumerate(columns):
                value = "⭐" if column == "★" and is_fav else row.get(column, "")
                cell = SortableTableItem(str(value))

                if column == "Item":
                    cell.setData(Qt.ItemDataRole.UserRole, product_id)

                elif column == "Buy Price":
                    cell.setData(
                        Qt.ItemDataRole.UserRole,
                        float(item.get("buy_price", 0))
                 )

                elif column == "Sell Price":
                    cell.setData(
                         Qt.ItemDataRole.UserRole,
                        float(item.get("sell_price", 0))
                )

                elif column == "Profit":
                    cell.setData(
                        Qt.ItemDataRole.UserRole,
                        float(item.get("spread", 0))
                )

                elif column == "Profit %":
                    cell.setData(
                        Qt.ItemDataRole.UserRole,
                        float(item.get("spread_percent", 0))
                )

                elif column == "Liquidity":
                    cell.setData(
                        Qt.ItemDataRole.UserRole,
                        float(item.get("liquidity", 0))
                )

                elif column == "Score":
                    cell.setData(
                        Qt.ItemDataRole.UserRole,
                        float(item.get("score", 0))
                )

                else:
                    cell.setData(
                        Qt.ItemDataRole.UserRole,
                        str(value).lower()
                )
                if column == "Item":
                    cell.setData(Qt.ItemDataRole.UserRole, product_id)

                if col_index == 1:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                else:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if column == "Profit":
                    self.color_profit_cell(cell, value)
                elif column in ["Profit %", "Score"]:
                    cell.setForeground(QColor("#66ccff"))
                elif column == "Tier":
                    self.color_tier_cell(cell, value)
                elif column == "Risk":
                    self.color_risk_cell(cell, value)
                elif column == "★" and is_fav:
                    cell.setForeground(QColor("#ffd700"))

                self.table.setItem(row_index, col_index, cell)

        self.table.setSortingEnabled(True)

    def color_profit_cell(self, cell, value):
        try:
            profit = float(str(value).replace(",", ""))
            if profit >= 1000:
                cell.setForeground(QColor("#00ff88"))
            elif profit >= 100:
                cell.setForeground(QColor("#66ff66"))
            elif profit > 0:
                cell.setForeground(QColor("#ffff66"))
            else:
                cell.setForeground(QColor("#ff5555"))
        except Exception:
            pass

    def color_tier_cell(self, cell, value):
        if value == "ELITE":
            cell.setForeground(QColor("#ffd700"))
        elif value == "GREAT":
            cell.setForeground(QColor("#00ff88"))
        elif value == "GOOD":
            cell.setForeground(QColor("#66ccff"))
        else:
            cell.setForeground(QColor("#999999"))

    def color_risk_cell(self, cell, value):
        if value == "Stable":
            cell.setForeground(QColor("#00ff88"))
        elif value == "Medium Risk":
            cell.setForeground(QColor("#ffaa00"))
        else:
            cell.setForeground(QColor("#ff4444"))
