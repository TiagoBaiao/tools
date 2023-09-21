import os
import sys
import time
import shutil
import logging
import yaml

# TODOS
# - Organise project folders according to typical python standards
# - Add tests

CONFIG_PATH = r'.\config.yaml'
CONFIG_TYPES = { 'folders_to_organise': list, 'media_extensions': list }

# Configure the logger to write to a file and to the console
def config_logger():
  logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s [%(levelname)s] %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    handlers = [
      logging.FileHandler("organize_media.log"),
      logging.StreamHandler(sys.stdout)
    ]
  )

# Log a fatal error and exit the script
def terminate_with_error(error_str):
  logging.error(error_str)
  input('\nPress any key to exit...')
  logging.info('Done!')
  sys.exit()

# Validate the configuration structure
def validate_config(config):
  if not isinstance(config, dict):
    terminate_with_error('The file "config.yaml" must have configuration variables defined. Script aborted.')

  for key in CONFIG_TYPES:
    if not key in config or not isinstance(config[key], CONFIG_TYPES[key]):
      terminate_with_error('The configuration file "config.yaml" must have a variable ' + key + ' of type ' + CONFIG_TYPES[key].__name__ + '. Script aborted.')

# Read the configuration file
def read_config_file(path):
  if not os.path.exists(path):
    terminate_with_error('Missing configuration file "config.yaml" in the same directory as "organise_media.py". Script aborted.')

  with open(path) as config_file:
    try:
      config = yaml.safe_load(config_file)
    except yaml.YAMLError as exception:
      terminate_with_error(exception)

  validate_config(config)

  return config

# Get the list of media files from the input directory path, based on the input media types array
def get_media_files(path, media_types):
  if os.path.isdir(path):
    for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
        filename, file_extension = os.path.splitext(file)

        if file_extension in media_types:
          yield file
  else:
    logging.warning('Failed to organise directory: ' + path + '. It does not exist.')

# Safely move files from one directory to another, by avoiding name clashes in the destination directory
# If there is a name clash, appends '_copy' to the filename (before the extension)
def safe_move(src_file_path, dest_path):
  src_dir, src_file_name = os.path.split(src_file_path)
  dest_file_name = src_file_name

  while os.path.exists(os.path.join(dest_path, dest_file_name)):
    dest_file_name = dest_file_name.replace('.', '_copy.', 1)

  if dest_file_name != src_file_name:
    logging.warning('Duplicated filename in destination directory: ' + dest_path + '.\n  Renamed a file to: ' + dest_file_name)

  shutil.move(src_file_path, os.path.join(dest_path, dest_file_name))

# Iterate over all media files in the directory to organise
def organise_media(dir, media_types):
  file_count = 0
  logging.info('Starting to organise files in: ' + dir + '...')

  for file in get_media_files(dir, media_types):
    creation_epoch = os.stat(os.path.join(dir, file)).st_mtime
    creation_date = time.strftime('%Y-%m_%B-%d', time.localtime(creation_epoch))

    date_elements = creation_date.split('-')
    year = date_elements[0]
    month = date_elements[1]

    destination_path = os.path.join(dir, year, month, '')
    os.makedirs(os.path.dirname(destination_path), exist_ok = True)

    file_path = os.path.join(dir, file)
    safe_move(file_path, destination_path)
    file_count += 1

  logging.info('Finished moving ' + str(file_count) + ' files!')

# Handles confirmation prompt answer by the user by either organising the media files in the input directories in different folders, or aborting the script
def handle_prompt_answer(answer, dirs, media_types):
  print('')

  if answer.lower() in ["yes"]:
    for dir in dirs:
      if os.path.isdir(dir): #TODO: Remove this if after creating functional tests
        try:
          organise_media(dir, media_types)
        except Exception as e:
          logging.error(e, exc_info=True)
      else:
        logging.warning('Failed to organise directory: ' + dir + '. It does not exist.')

      print('')

  else:
    logging.info('Script aborted.')

  input('\nPress any key to exit...')

# Main script logic
def main():
  print('')

  config_logger()
  logging.info('Starting the organise_media script...')

  config = read_config_file(CONFIG_PATH)
  target_dirs = config['folders_to_organise']
  media_types = config['media_extensions']

  # Confirmation prompt
  logging.info('Will organise all files with extension:\n- ' + "\n- ".join(media_types) + '\n\nin the following folders:\n- ' + "\n- ".join(target_dirs) + '\n\nby creation_date in "year/month/" directories.')
  answer = input('\nType [yes] to continue, or something else to abort\n\n>> ')
  handle_prompt_answer(answer, target_dirs, media_types)

  logging.info('Done!')

# Run the script
if __name__ == '__main__':
  main()
