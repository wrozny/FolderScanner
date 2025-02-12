import os
import sys

from scanner import Scanner, format_bytes
from colors import get_gradient_value, DEFAULT_GRADIENT

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenu, QVBoxLayout, QWidget, QPushButton, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QLabel, QHBoxLayout
)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label_memory = None
        self.label_dirs = None
        self.label_files = None
        self.cancel_scan_button = None
        self.start_scan_button = None
        self.dir_button = None
        self.status_bar = None
        self.tree_widget = None
        self.target_directory = None
        self.setWindowTitle("Directory Scanner")
        self.setGeometry(100, 100, 800, 600)
        self.directory_scanner = Scanner()
        self.directory_scanner.bind_on_scanned_finished(self.on_scan_finished)
        self.directory_scanner.bind_label_update_callback(self.update_labels)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(["Directory", "Size (Bytes)"])
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.tree_widget)
        self.create_buttons(layout)
        self.status_bar = self.statusBar()
        self.create_menu()

    def create_buttons(self, layout):
        self.dir_button = QPushButton("Choose Directory", self)
        self.dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.dir_button)

        self.start_scan_button = QPushButton("Start Scan", self)
        self.start_scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.start_scan_button)

        self.cancel_scan_button = QPushButton("Cancel Scan", self)
        self.cancel_scan_button.clicked.connect(self.cancel_scan)
        layout.addWidget(self.cancel_scan_button)

        self.label_files = QLabel("Files: 0", self)
        self.label_dirs = QLabel("Directories: 0", self)
        self.label_memory = QLabel("Memory: 0b", self)

        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.label_files)
        stats_layout.addWidget(self.label_dirs)
        stats_layout.addWidget(self.label_memory)

        layout.addLayout(stats_layout)

    def create_menu(self):
        file_menu = QMenu("File", self)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_action)
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_action)

        file_menu.addAction(save_action)
        file_menu.addAction(load_action)

        self.menuBar().addMenu(file_menu)

    def update_labels(self, files: int, directories: int, bytes: int):
        self.label_dirs.setText(f"Directories: {directories}")
        self.label_files.setText(f"Files: {files if files >= 0 else '?'}")
        self.label_memory.setText("Memory: {}".format(format_bytes(bytes)))

    def on_scan_finished(self):
        self.status_bar.showMessage("Rendering tree...")
        self.set_tree(self.directory_scanner.scan_result)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.target_directory = dir_path

    def show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item:
            menu = QMenu(self)
            copy_action = QAction("Copy Full Path", self)
            copy_action.triggered.connect(lambda: self.copy_full_path(item))
            menu.addAction(copy_action)
            menu.exec(self.tree_widget.viewport().mapToGlobal(position))

    def copy_full_path(self, item):
        full_path = item.data(0, Qt.ItemDataRole.UserRole)
        clipboard = QApplication.clipboard()
        clipboard.setText(full_path)
        self.status_bar.showMessage(f"Copied: {full_path}", 2000)

    def set_tree(self, scanned_data):
        self.tree_widget.clear()
        try:
            dir_name = scanned_data[0]
            dir_size = scanned_data[1]
            dir_children = scanned_data[2]
            parent_item = QTreeWidgetItem([dir_name, format_bytes(dir_size)])
            parent_item.setData(0, Qt.ItemDataRole.UserRole, dir_name)
            parent_item.setData(1, Qt.ItemDataRole.UserRole, dir_size)

            self.tree_widget.addTopLevelItem(parent_item)
            self.add_children(parent_item, dir_children)
            self.status_bar.showMessage("Tree rendered successfully!")
        except Exception as e:
            self.status_bar.showMessage(f"Failed to render the tree! Error: {e}")

    def add_children(self, parent_item, children):
        sorted_data = sorted(children, key=lambda x: x[1], reverse=True)
        for child in sorted_data:
            dir_path = child[0]
            dir_size = child[1]
            dir_children = child[2]
            dir_name = os.path.basename(dir_path)
            child_item = QTreeWidgetItem([dir_name, format_bytes(dir_size)])

            parent_dir_size = parent_item.data(1, Qt.ItemDataRole.UserRole)
            parent_dir_memory_use_percentage = (dir_size / parent_dir_size) if parent_dir_size > 0 else 0

            color = get_gradient_value(DEFAULT_GRADIENT, parent_dir_memory_use_percentage)

            child_item.setBackground(0, QColor(*color))

            child_item.setData(0, Qt.ItemDataRole.UserRole, dir_path)
            child_item.setData(1, Qt.ItemDataRole.UserRole, dir_size)
            parent_item.addChild(child_item)
            self.add_children(child_item, dir_children)

    def start_scan(self):
        if self.directory_scanner.is_scanning:
            self.status_bar.showMessage("Directory is being scanned!")
            return

        if self.target_directory:
            self.status_bar.showMessage("Scanning...")
            self.directory_scanner.start_scan(self.target_directory)
            return
        self.status_bar.showMessage("Choose a directory!")

    def cancel_scan(self):
        if self.directory_scanner.is_scanning:
            self.status_bar.showMessage("Canceling scan...")
            self.directory_scanner.end_scan()

    def save_action(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.json)")
        self.status_bar.showMessage("Saving...")
        if self.directory_scanner.scan_result is not None:
            self.directory_scanner.save_scan_data(file_path)
            self.status_bar.showMessage("Saved successfully!")

    def load_action(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.json)")
        self.status_bar.showMessage("Loading...")

        if not os.path.isfile(file_path):
            self.status_bar.showMessage("Failed to load! Invalid directory!")
            return

        self.directory_scanner.load_scan_data(file_path)
        self.status_bar.showMessage("Loaded successfully!")
        self.set_tree(self.directory_scanner.scan_result)


def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
