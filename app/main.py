import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from downloader import HuggingFaceModelDownloader
from settings import SettingsDialog
from dotenv import load_dotenv
import os
import threading

class ModelDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize the window
        self.setWindowTitle("HuggingFace Model Downloader")
        self.setFixedSize(400, 300)  # Set fixed window size

        # Layout and widgets
        self.layout = QVBoxLayout()

        # Settings button at the top
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setFixedWidth(100)  # Set fixed width for the button
        self.settings_button.clicked.connect(self.show_token_input_dialog)
        self.layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label for repo ID input
        self.repo_label = QLabel("Enter HuggingFace Repository ID:", self)
        self.layout.addWidget(self.repo_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Text box for repo ID
        self.repo_input = QLineEdit(self)
        self.repo_input.setFixedWidth(350)  # Set fixed width for the text box
        self.repo_input.setPlaceholderText("e.g., meta-llama/Llama-3.2-1B")
        self.layout.addWidget(self.repo_input, alignment=Qt.AlignmentFlag.AlignLeft)

        # Status label
        self.status_label = QLabel("Enter repository ID and click download.", self)
        self.status_label.setWordWrap(True)  # Enable text wrapping
        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Cancel button
        self.cancel_button = QPushButton("Cancel Download", self)
        self.cancel_button.setFixedWidth(150)  # Set fixed width for the button
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setVisible(False)
        self.layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Download button
        self.download_button = QPushButton("Download Model", self)
        self.download_button.setFixedWidth(150)  # Set fixed width for the button
        self.download_button.clicked.connect(self.download_model)
        self.layout.addWidget(self.download_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the layout
        self.setLayout(self.layout)

        # Initialize downloader without a parent
        self.downloader = HuggingFaceModelDownloader()
        self.downloader.finished.connect(self.download_finished)

        # Check for token on startup
        self.check_token()

    def check_token(self):
        """Check if HuggingFace token exists."""
        load_dotenv(os.path.join(os.path.expanduser('~'), '.huggingface_downloader.env'))
        if not os.getenv('HUGGINGFACE_TOKEN'):
            self.status_label.setText("Token not found. Please set your HuggingFace access token in Settings.")
            self.download_button.setEnabled(False)
        else:
            self.status_label.setText("Token saved successfully. You can now download models.")
            self.download_button.setEnabled(True)

    def show_token_input_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.move(self.x() + 50, self.y())  # Position the dialog 50 pixels right and down from the main window
        
        if dialog.exec():
            # Reload token after dialog
            load_dotenv(os.path.join(os.path.expanduser('~'), '.huggingface_downloader.env'))
            if os.getenv('HUGGINGFACE_TOKEN'):
                self.status_label.setText("Token saved successfully. You can now download models.")
                self.download_button.setEnabled(True)
            else:
                self.status_label.setText("Token not found. Please set your HuggingFace access token in Settings.")
                self.download_button.setEnabled(False)

    def download_model(self):
        """Download model from Hugging Face."""
        if not os.getenv('HUGGINGFACE_TOKEN'):
            QMessageBox.warning(self, "Token Required", 
                              "Please set your HuggingFace access token in Settings first.")
            self.show_token_input_dialog()
            return

        self.repo_id = self.repo_input.text().strip()
        
        if not self.repo_id:
            QMessageBox.warning(self, 
                              "Input Required", 
                              "Please enter a repository ID before downloading.",
                              QMessageBox.StandardButton.Ok)
            return
        if os.getenv('MODEL_SAVE_DIR'):
            self.save_path = os.getenv('MODEL_SAVE_DIR')
            
        self.status_label.setText("Downloading model...")
        self.cancel_button.setVisible(True)

        def run_download():
            try:
                self.downloader.download_model(self.repo_id, self.save_path)
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")

        # Run in separate thread to avoid freezing UI
        self.download_thread = threading.Thread(target=run_download)
        self.download_thread.start()

    def download_finished(self, success, message):
        """Handle the completion of the download."""
        if success:
            self.status_label.setText(f"Model downloaded to: {message}")
        else:
            self.status_label.setText(f"Error: {message}")
        self.cancel_button.setVisible(False)

    def cancel_download(self):
        """Cancel the download process."""
        self.downloader.cancel_download()
        if self.download_thread.is_alive():
            self.download_thread.join()
        self.status_label.setText("Download cancelled.")
        self.cancel_button.setVisible(False)

if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)

    # Create the main window
    window = ModelDownloaderApp()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec())
