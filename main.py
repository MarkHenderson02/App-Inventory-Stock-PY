import sys
import csv
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QLabel, QHBoxLayout, QHeaderView
)
from PyQt6.QtCore import QTimer, QDate
from fpdf import FPDF

# File to store inventory data
DATA_FILE = "inventory_data.csv"
REPORT_FILE = "monthly_report.pdf"

class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Stock Product Paint")
        self.setGeometry(100, 100, 600, 400)

        # Layouts
        layout = QVBoxLayout()

        # Input fields
        self.code_input = QLineEdit(self)
        self.code_input.setPlaceholderText("Enter Product Code")
        self.color_input = QLineEdit(self)
        self.color_input.setPlaceholderText("Enter Product Color")
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Product Name")

        # Buttons
        self.submit_button = QPushButton("Submit New Item", self)
        self.submit_button.clicked.connect(self.submit_item)
        self.add_button = QPushButton("Add Stock (+)", self)
        self.subtract_button = QPushButton("Reduce Stock (-)", self)
        self.generate_report_button = QPushButton("Generate Monthly Report", self)
        self.add_button.clicked.connect(self.add_stock)
        self.subtract_button.clicked.connect(self.reduce_stock)
        self.generate_report_button.clicked.connect(self.generate_report)

        # Stock label
        self.stock_label = QLabel("Stock: 0", self)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Product Code", "Color", "Name", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Layout arrangement
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.code_input)
        input_layout.addWidget(self.color_input)
        input_layout.addWidget(self.name_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.subtract_button)
        button_layout.addWidget(self.generate_report_button)
        button_layout.addWidget(self.stock_label)

        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Load existing data
        self.load_data()

        # Auto-save timer (every 60 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_data)
        self.timer.start(60000)

    def load_data(self):
        """ Load inventory data from the file """
        if not os.path.exists(DATA_FILE):
            return
        
        self.table.setRowCount(0)
        with open(DATA_FILE, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                self.add_row(row[0], row[1], row[2], int(row[3]))

    def save_data(self):
        """ Save current inventory data to a file every minute """
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for row in range(self.table.rowCount()):
                writer.writerow([
                    self.table.item(row, 0).text(),
                    self.table.item(row, 1).text(),
                    self.table.item(row, 2).text(),
                    self.table.item(row, 3).text(),
                ])
        print("Data saved automatically.")

    def add_row(self, code, color, name, stock):
        """ Add a new row to the table """
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem(code))
        self.table.setItem(row_count, 1, QTableWidgetItem(color))
        self.table.setItem(row_count, 2, QTableWidgetItem(name))
        self.table.setItem(row_count, 3, QTableWidgetItem(str(stock)))

    def get_selected_row(self):
        """ Get the selected row index """
        selected = self.table.currentRow()
        if selected == -1:
            return None
        return selected

    def submit_item(self):
        """ Submit a new item to the inventory """
        code = self.code_input.text().strip()
        color = self.color_input.text().strip()
        name = self.name_input.text().strip()
        
        if code and color and name:
            self.add_row(code, color, name, 0)
            self.code_input.clear()
            self.color_input.clear()
            self.name_input.clear()
            self.save_data()
        else:
            print("Please enter all fields correctly.")

    def add_stock(self):
        """ Increase stock of selected product """
        selected_row = self.get_selected_row()
        if selected_row is not None:
            current_stock = int(self.table.item(selected_row, 3).text())
            current_stock += 1
            self.table.setItem(selected_row, 3, QTableWidgetItem(str(current_stock)))
            self.stock_label.setText(f"Stock: {current_stock}")

    def reduce_stock(self):
        """ Decrease stock of selected product """
        selected_row = self.get_selected_row()
        if selected_row is not None:
            current_stock = int(self.table.item(selected_row, 3).text())
            if current_stock > 0:
                current_stock -= 1
                self.table.setItem(selected_row, 3, QTableWidgetItem(str(current_stock)))
                self.stock_label.setText(f"Stock: {current_stock}")
    
    def generate_report(self):
        """ Generate a monthly report and save as PDF """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"Inventory Report - {QDate.currentDate().toString('MMMM yyyy')}", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Product Code", 1)
        pdf.cell(50, 10, "Color", 1)
        pdf.cell(50, 10, "Name", 1)
        pdf.cell(30, 10, "Stock", 1)
        pdf.ln()
        pdf.set_font("Arial", size=12)
        for row in range(self.table.rowCount()):
            pdf.cell(50, 10, self.table.item(row, 0).text(), 1)
            pdf.cell(50, 10, self.table.item(row, 1).text(), 1)
            pdf.cell(50, 10, self.table.item(row, 2).text(), 1)
            pdf.cell(30, 10, self.table.item(row, 3).text(), 1)
            pdf.ln()
        pdf.output(REPORT_FILE)
        print(f"Monthly report saved as {REPORT_FILE}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec())
