import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel

from ui.widgets.glow_button import GlowButton


class ApiPage(QWidget):
    def __init__(self):
        super().__init__()

        self.raw_debug_text = ""
        self.numbered_debug_text = ""

        layout = QVBoxLayout()
        layout.setContentsMargins(38, 38, 38, 38)
        self.setLayout(layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search API JSON: bank_account, balance, coin_purse, SKILL_COMBAT"
        )

        self.search_button = GlowButton("Search")
        self.balance_button = GlowButton("Search All Balances")
        self.clear_button = GlowButton("Clear")

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("color: #b8c7dd; font-size: 13px;")

        row = QHBoxLayout()
        row.addWidget(self.search_box)
        row.addWidget(self.search_button)
        row.addWidget(self.balance_button)
        row.addWidget(self.clear_button)

        from PyQt6.QtWidgets import QTextEdit
        self.output = QTextEdit()

        layout.addLayout(row)
        layout.addWidget(self.result_label)
        layout.addWidget(self.output)

        self.search_button.clicked.connect(self.search)
        self.balance_button.clicked.connect(self.search_all_balances)
        self.clear_button.clicked.connect(self.clear_search)
        self.search_box.returnPressed.connect(self.search)

    def add_line_numbers(self, text: str) -> str:
        return "\n".join(
            f"{str(i + 1).rjust(6)} | {line}"
            for i, line in enumerate(text.splitlines())
        )

    def set_debug_data(self, data: dict):
        self.raw_debug_text = json.dumps(data, indent=2)
        self.numbered_debug_text = self.add_line_numbers(self.raw_debug_text)
        self.output.setText(self.numbered_debug_text)
        self.result_label.setText("Raw API JSON loaded with line numbers.")

    def set_error(self, error: str):
        text = f"Error:\n\n{error}"
        self.raw_debug_text = text
        self.numbered_debug_text = text
        self.output.setText(text)
        self.result_label.setText("Error loading API data.")

    def search(self):
        query = self.search_box.text().strip()

        if not query:
            self.output.setText(self.numbered_debug_text)
            self.result_label.setText("Enter a search term.")
            return

        lines = self.raw_debug_text.splitlines()
        matches = []

        for i, line in enumerate(lines, start=1):
            if query.lower() in line.lower():
                start = max(1, i - 4)
                end = min(len(lines), i + 4)

                matches.append(f"\n--- Match near line {i} ---")

                for n in range(start, end + 1):
                    matches.append(f"{str(n).rjust(6)} | {lines[n - 1]}")

        if matches:
            self.output.setText("\n".join(matches))
            self.result_label.setText(f"Found {len(matches)} matches for: {query}")
        else:
            self.output.setText(f"No matches found for: {query}")
            self.result_label.setText("0 matches.")

    def search_all_balances(self):
        keywords = [
            "balance",
            "banking",
            "bank",
            "bank_account",
            "coin_purse",
            "purse",
        ]

        lines = self.raw_debug_text.splitlines()
        matches = []

        for i, line in enumerate(lines, start=1):
            if any(keyword in line.lower() for keyword in keywords):
                start = max(1, i - 3)
                end = min(len(lines), i + 3)

                matches.append(f"\n--- Balance-related match near line {i} ---")

                for n in range(start, end + 1):
                    matches.append(f"{str(n).rjust(6)} | {lines[n - 1]}")

        if matches:
            self.output.setText("\n".join(matches))
            self.result_label.setText(
                f"Found {len(matches)} balance-related matches."
            )
        else:
            self.output.setText("No balance-related matches found.")
            self.result_label.setText("0 matches.")

    def clear_search(self):
        self.search_box.clear()
        self.output.setText(self.numbered_debug_text)
        self.result_label.setText("Search cleared.")
