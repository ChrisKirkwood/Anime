import logging
import os

# Set up Google Cloud credentials
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Anime/credentials.json"

# Ensure the log directory exists
log_directory = "D:/Anime/log"
os.makedirs(log_directory, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=os.path.join(log_directory, 'backend.log'),
    level=logging.DEBUG,  # Set to DEBUG for detailed logging
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'  # Append to the log file
)

# Console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.getLogger().addHandler(console_handler)

logging.info("Logging setup complete.")
