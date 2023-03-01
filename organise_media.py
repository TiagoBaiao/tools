import os
import sys
import time
import shutil
import logging


DIR_TO_ORGANISE = r'C:\test1\test2\test3'
MEDIA_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.mp4']

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

# Get the list of media files from the input directory path, based on the input media types array
def get_media_files(path, media_types):
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      filename, file_extension = os.path.splitext(file)

      if file_extension in media_types:
        yield file

# Safely move files from one directory to another, by avoiding name clashes in the destination directory
# If there is a name clash, appends '_copy' to the filename (before the extension)
def safe_move(file_path, dest_path):
  src_dir, file_name = os.path.split(file_path)
  duplicated_file_name = False

  while os.path.exists(os.path.join(dest_path, file_name)):
    duplicated_file_name = True
    file_name = file_name.replace('.', '_copy.', 1)

  if duplicated_file_name:
    logging.warning('Duplicated filename in destination directory: ' + dest_path + '.\n  Renamed a file to: ' + file_name)

  shutil.move(file_path, os.path.join(dest_path, file_name))

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

# Handles confirmation prompt answer by the user by either organising the media files in the input directory in different folders, or aborting the script
def handle_prompt_answer(answer, dir, media_types):
  print('')

  if answer.lower() in ["yes"]:
    try:
      organise_media(dir, media_types)
    except Exception as e:
      logging.error(e, exc_info=True)
  else:
    logging.info('Script aborted.')

  input('\nPress any key to exit...')

# Main script logic
def main():
  print('')
  target_dir = DIR_TO_ORGANISE
  media_types = MEDIA_EXTENSIONS

  config_logger()
  logging.info('Starting the organise_media script...')

  if os.path.isdir(target_dir):
    # Confirmation prompt
    answer = input('\nWill organise all files in: "' + target_dir + '" by creation_date in "year/month/" directories.\nType [yes] to continue, or something else to abort\n\n>> ')
    handle_prompt_answer(answer, target_dir, media_types)
  else:
    logging.error('The configured directory to organise: ' + target_dir + ', does not exist. Script aborted...')

  logging.info('Done!')

# Run the script
main()
