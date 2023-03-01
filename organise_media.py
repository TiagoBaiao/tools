import os
import sys
import time
import shutil
import logging


DIR_TO_ORGANISE = 'C:/test1/test2/test3'
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

# Get the list of media files from the input directory path, based on the MEDIA_EXTENSIONS array
def files(path):
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      filename, file_extension = os.path.splitext(file)

      if file_extension in MEDIA_EXTENSIONS:
        yield file

# Safely move files from one directory to another, by avoiding name clashes in the destination directory
# If there is a name clash, appends '_copy' to the filename before the extension
def safe_move(src_path, dest_path):
  dir, f_name = os.path.split(src_path)
  duplicated_f_name = False

  while os.path.exists(os.path.join(dest_path, f_name)):
    duplicated_f_name = True
    split_f_name = f_name.split('.', 1)
    f_name = split_f_name[0] + '_copy.' + split_f_name[1]

  if duplicated_f_name:
    logging.warning('Duplicated filename in destination directory: "' + dest_path + '".\n  Renamed a file to: ' + f_name)

  shutil.move(src_path, os.path.join(dest_path, f_name))

# Iterate over all files in the directory to organise
def organise_media():
  file_count = 0
  logging.info('Starting to organise files in "' + DIR_TO_ORGANISE + '"')

  for file in files(DIR_TO_ORGANISE):
      creation_epoch = os.stat(os.path.join(DIR_TO_ORGANISE, file)).st_mtime
      creation_date = time.strftime('%Y-%m_%B-%d', time.localtime(creation_epoch))

      date_elements = creation_date.split('-')
      year = date_elements[0]
      month = date_elements[1]

      destination_path = DIR_TO_ORGANISE + '/' + year + '/' + month + '/'
      os.makedirs(os.path.dirname(destination_path), exist_ok = True)

      file_path = DIR_TO_ORGANISE + '/' + file
      safe_move(file_path, destination_path)
      file_count += 1

  logging.info('Finished moving ' + str(file_count) + ' files!')

# Main script logic
def main():
  # Confirmation prompt
  answer = input('\nWill organise all files in: "' + DIR_TO_ORGANISE + '" by creation_date in "year/month/" directories.\nType [yes] to continue, or something else to abort\n\n>> ')

  if answer.lower() in ["yes"]:
    print(' ')
    config_logger()

    try:
      organise_media()

    except Exception as e:
      logging.error(e, exc_info=True)

    input('\nPress any key to exit...')

  else:
    input('\nScript aborted. Press any key to exit...')

# Run the script
main()
