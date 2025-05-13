import logging
from pathlib import Path

log_file = Path(__file__).parent / "logs.log"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cook4You logger")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(level=logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)