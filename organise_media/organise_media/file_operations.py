import logging
import os
import shutil
import time

# Iterate over all media files in the directory to organise
def organise_media(dir, media_types):
  file_count = 0
  logging.info(f'Starting to organise files in: {dir}...')

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

    logging.info(f'Finished moving {str(file_count)} files!')

# Get the list of media files from the input directory path, based on the input media types array
def get_media_files(dir, media_types):
  if os.path.isdir(dir):
    for file in os.listdir(dir):
      if os.path.isfile(os.path.join(dir, file)):
        filename, file_extension = os.path.splitext(file)

        if file_extension in media_types:
          yield file
  else:
    logging.warning(f'Failed to organise directory: {dir}. It does not exist.')

# Safely move files from one directory to another, by avoiding name clashes in the destination directory
# If there is a name clash, appends '_copy' to the filename (before the extension)
def safe_move(src_file_path, dest_path):
  src_dir, src_file_name = os.path.split(src_file_path)
  dest_file_name = src_file_name

  while os.path.exists(os.path.join(dest_path, dest_file_name)):
    dest_file_name = dest_file_name.replace('.', '_copy.', 1)

  if dest_file_name != src_file_name:
    logging.warning(f'Duplicated filename in destination directory: {dest_path}.\n  Renamed a file to: {dest_file_name}')

  shutil.move(src_file_path, os.path.join(dest_path, dest_file_name))