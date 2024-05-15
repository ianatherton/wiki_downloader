import os
import logging
from src.downloader import download_wiki
from config import base_url, base_dir, progress_file

# Configure logging
logging.basicConfig(filename='download.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

os.makedirs(base_dir, exist_ok=True)
download_wiki(base_url, base_dir, progress_file)