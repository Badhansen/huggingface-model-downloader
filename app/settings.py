from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFileDialog)
from dotenv import set_key, load_dotenv
from huggingface_hub import HfApi, login
from PyQt6.QtCore import Qt
import requests
import os


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HuggingFace Token Setup")
        
        self.setFixedSize(400, 300)  # Set fixed window size
        
        self.layout = QVBoxLayout()
        
        # Add instructions
        instructions = QLabel(
            "Please enter your HuggingFace access token.\n"
            "You can find this at: https://huggingface.co/settings/tokens",
            self
        )
        self.layout.addWidget(instructions, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Token input field
        self.token_input = QLineEdit(self)
        self.token_input.setFixedWidth(350)  # Set fixed width for the input field
        self.token_input.setPlaceholderText("Enter your HuggingFace token")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.token_input, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Model directory save path input field
        self.layout.addWidget(QLabel("Enter model save directory:", self), alignment=Qt.AlignmentFlag.AlignLeft)
        self.model_dir_layout = QHBoxLayout()
        self.model_dir_input = QLineEdit(self)
        self.model_dir_input.setPlaceholderText("Enter model save directory")
        self.model_dir_layout.addWidget(self.model_dir_input)
        
        # Browse button for model directory
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_model_dir)
        self.model_dir_layout.addWidget(self.browse_button)
        
        self.layout.addLayout(self.model_dir_layout)
        
        # Save button
        self.save_button = QPushButton("Save Settings", self)
        self.save_button.setFixedWidth(150)  # Set fixed width for the button
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(self.layout)
        self.load_settings()
    
    def browse_model_dir(self):
        """Open a file dialog to select the model save directory."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Model Save Directory")
        if dir_path:
            self.model_dir_input.setText(dir_path)
    
    def save_settings(self):
        token = self.token_input.text().strip()
        model_dir = self.model_dir_input.text().strip()
        
        # Warn and prevent closing if the token is empty
        if not token:
            QMessageBox.warning(self, "Error", "Please enter a valid token")
            return
        
        # Set default model directory if none is provided
        if not model_dir:
            model_dir = os.path.join(os.path.expanduser('~'), 'models')  # Default to 'models' folder in user's home directory
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)  # Create the 'models' folder if it doesn't exist

        try:
            # Validate the token
            self.api = HfApi(token=token)
            
            if not self.validate_token(token=token):
                return

            # Create .env file in home directory
            env_path = os.path.join(os.path.expanduser('~'), '.huggingface_downloader.env')
            print(f"Saving settings to: {env_path}")  # Debug print
            set_key(env_path, 'HUGGINGFACE_TOKEN', token)
            set_key(env_path, 'MODEL_SAVE_DIR', model_dir)
            os.chmod(env_path, 0o600)  # Set secure file permissions
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                QMessageBox.critical(self, "Error", "Invalid token. Please enter a valid HuggingFace token.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to validate token: {str(e)}")
            print(f"Error: {str(e)}")  # Debug print
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            print(f"Error: {str(e)}")  # Debug print
    
    def load_settings(self):
        load_dotenv()
        token = os.getenv('HUGGINGFACE_TOKEN')
        model_dir = os.getenv('MODEL_SAVE_DIR')
        if token:
            self.token_input.setText(token)
        if model_dir:
            self.model_dir_input.setText(model_dir)

    def validate_token(self, token: str):
        """Validate the HuggingFace token."""
        try:
            login(token=token)
            self.api.whoami()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save token: Invalid token, Please follow instructions!")
            print(f"Error: {str(e)}")  # Debug print
            return False