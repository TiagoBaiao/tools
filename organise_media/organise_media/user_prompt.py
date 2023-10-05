import logging
import os
import sys
from .configuration_reader import read_config_file
from .file_operations import organise_media
from .logger_config import config_logger

RELATIVE_CONFIG_FILE_PATH = "../config.yaml"

# Main script logic
def run():
  config = init()

  target_dirs = config['folders_to_organise']
  media_types = config['media_extensions']

  # Confirmation prompt
  logging.info(''.join([
    'Will organise all files with extension:\n- ',
    '\n- '.join(media_types),
    '\n\nin the following folders:\n- ',
    '\n- '.join(target_dirs),
    '\n\nby creation_date in "year/month/" directories.'
  ]))
  answer = input('\nType [yes] to continue, or something else to abort\n\n>> ')

  handle_prompt_answer(answer, target_dirs, media_types)

  input('\nPress any key to exit...')
  logging.info('Done!')

# Initial operations
def init():
  print('')

  config_logger()
  logging.info('Starting the organise_media script...')

  config_file_path = os.path.join(os.path.dirname(__file__), RELATIVE_CONFIG_FILE_PATH)
  config, valid, error_msg = read_config_file(config_file_path)
  if not valid:
    terminate_with_error(error_msg)

  return config

# Log a fatal error and exit the script
def terminate_with_error(error_str):
  logging.error(error_str)
  input('\nPress any key to exit...')
  logging.info('Done!')
  sys.exit()

# Handles confirmation prompt answer by the user by either organising the media files in the input directories in different folders, or aborting the script
def handle_prompt_answer(answer, dirs, media_types):
  print('')

  if answer.lower() in ["yes"]:
    for dir in dirs:
      try:
        organise_media(dir, media_types)
      except Exception as e:
        logging.error(e, exc_info=True)

      print('')

  else:
    logging.info('Script aborted.')