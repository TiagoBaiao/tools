import logging
import os
import sys

RELATIVE_LOG_DIR_PATH = "../log/"
LOG_FILE_NAME = "organize_media.log"

# Configure the logger to write to a file and to the console
def config_logger():
  log_dir_path = os.path.join(os.path.dirname(__file__), RELATIVE_LOG_DIR_PATH)

  if not os.path.exists(log_dir_path):
    os.makedirs(log_dir_path)

  logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s [%(levelname)s] %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    handlers = [
      logging.FileHandler(os.path.join(log_dir_path, LOG_FILE_NAME)),
      logging.StreamHandler(sys.stdout)
    ]
  )