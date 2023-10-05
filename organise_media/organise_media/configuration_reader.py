import os
import yaml

# Read the configuration file
def read_config_file(path):
  config = { 'folders_to_organise': list(), 'media_extensions': list() }

  if not os.path.exists(path):
    return config, bool(False), str('Missing configuration file "config.yaml" in the root directory of the project. Script aborted.')

  with open(path) as config_file:
    try:
      config = yaml.safe_load(config_file)
    except yaml.YAMLError as exception:
      return config, bool(False), exception

  return config, *is_valid_config(config)

# Validate the configuration structure
def is_valid_config(config):
  config_types = { 'folders_to_organise': list, 'media_extensions': list }

  if not isinstance(config, dict):
    return bool(False), str('The file "config.yaml" must have configuration variables defined. Script aborted.')

  for key in config_types:
    if not key in config or not isinstance(config[key], config_types[key]):
      return bool(False), str(f'The configuration file "config.yaml" must have a variable {key} of type {config_types[key].__name__}. Script aborted.')

  return bool(True), str()