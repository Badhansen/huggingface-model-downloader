from huggingface_hub import HfApi, hf_hub_download, login
from PyQt6.QtCore import pyqtSignal, QObject
from dotenv import load_dotenv
import os

class HuggingFaceModelDownloader(QObject):
    """Securely download Hugging Face models with retries."""
    
    finished = pyqtSignal(bool, str)
    
    def __init__(self):
        """Initialize with Hugging Face API token."""
        super().__init__()
        self.cancelled = False
        
    def check_and_get_token(self):
        """Check if HuggingFace token exists and prompt user if not."""
        load_dotenv(os.path.join(os.path.expanduser('~'), '.huggingface_downloader.env'))
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN', "")
        
        if not self.hf_token:
            raise ValueError("HUGGINGFACE_TOKEN not found! Please set up your token.")
        
        self.api = HfApi(token=self.hf_token)
        login(token=self.hf_token)

    def download_model(self, repo_id: str, save_path: str = "models/"):
        """Download a model."""
        self.check_and_get_token()  # Ensure token is checked before download
        
        model_path = os.path.join(save_path, repo_id.split("/")[-1])
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        try:
            self.cancelled = False
            files = self.api.list_repo_files(repo_id=repo_id)
            
            for file in files:
                if self.cancelled:
                    raise Exception("Download cancelled by user")
                hf_hub_download(repo_id=repo_id, filename=file, local_dir=model_path)
            
            if self.cancelled:
                raise Exception("Download cancelled by user")
            self.finished.emit(True, model_path)
            return model_path
        except Exception as e:
            self.finished.emit(False, f"Download failed: {str(e)}")

    def cancel_download(self):
        """Cancel the download process."""
        self.cancelled = True
