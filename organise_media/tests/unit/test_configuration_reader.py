import yaml
from organise_media.organise_media.configuration_reader import is_valid_config, read_config_file
from organise_media.tests.test_helpers import FakeFile, create_test_file

def test_is_valid_config_returns_false_for_wrong_input_type():
    config = ["folders_to_organise", "media_extensions"]
    valid, error_msg = is_valid_config(config)

    assert not valid
    assert error_msg == 'The file "config.yaml" must have configuration variables defined. Script aborted.'

def test_is_valid_config_returns_false_for_empty_config():
    config = {}
    valid, error_msg = is_valid_config(config)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable folders_to_organise of type list. Script aborted.'

def test_is_valid_config_returns_false_when_missing_folders_to_organise():
    config = { 'media_extensions': list() }
    valid, error_msg = is_valid_config(config)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable folders_to_organise of type list. Script aborted.'

def test_is_valid_config_returns_false_when_missing_media_extensions():
    config = { 'folders_to_organise': list() }
    valid, error_msg = is_valid_config(config)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable media_extensions of type list. Script aborted.'

def test_is_valid_config_returns_false_when_folders_to_organise_is_of_wrong_type():
    config = { 'folders_to_organise': {}, 'media_extensions': list() }
    valid, error_msg = is_valid_config(config)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable folders_to_organise of type list. Script aborted.'

def test_is_valid_config_returns_false_when_media_extensions_is_of_wrong_type():
    config = { 'folders_to_organise': list(), 'media_extensions': {} }
    valid, error_msg = is_valid_config(config)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable media_extensions of type list. Script aborted.'

def test_is_valid_config_returns_true_when_config_is_complete_with_correct_types():
    config = { 'folders_to_organise': list(), 'media_extensions': list() }
    valid, error_msg = is_valid_config(config)

    assert valid

def test_read_config_file_returns_false_for_non_existant_config_file():
    config_file = FakeFile("./test_dir/config.yaml")

    config, valid, error_msg = read_config_file(config_file.path)

    assert not valid
    assert error_msg == 'Missing configuration file "config.yaml" in the same directory as "run_organise_media.py". Script aborted.'

def test_read_config_file_returns_false_for_empty_yaml_file(fs):
    config_file = FakeFile("./test_dir/config.yaml")

    create_test_file(fs, config_file)
    config, valid, error_msg = read_config_file(config_file.path)

    assert not valid
    assert error_msg == 'The file "config.yaml" must have configuration variables defined. Script aborted.'

def test_read_config_file_returns_false_for_invalid_yaml_file(fs):
    config_file = FakeFile(
        "./test_dir/config.yaml",
        "".join([
            "media_extensions:  - .jpg  - .png"
        ])
    )

    create_test_file(fs, config_file)
    config, valid, error_msg = read_config_file(config_file.path)

    assert not valid
    assert isinstance(error_msg, yaml.YAMLError)

def test_read_config_file_returns_false_for_yaml_file_misisng_folders_to_organise(fs):
    config_file = FakeFile(
        "./test_dir/config.yaml",
        "".join([
            "media_extensions:\n",
            "    - .jpg\n",
            "    - .png\n"
        ])
    )

    create_test_file(fs, config_file)
    config, valid, error_msg = read_config_file(config_file.path)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable folders_to_organise of type list. Script aborted.'

def test_read_config_file_returns_false_for_yaml_file_misisng_media_extensions(fs):
    config_file = FakeFile(
        "./test_dir/config.yaml",
        "".join([
            "folders_to_organise:\n",
            "    - D:\\test\\data\n",
            "    - E:\\some\\folder\n"
        ])
    )

    create_test_file(fs, config_file)
    config, valid, error_msg = read_config_file(config_file.path)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable media_extensions of type list. Script aborted.'

def test_read_config_file_returns_true_and_config_matching_yaml_attributes(fs):
    config_file = FakeFile(
        "./test_dir/config.yaml",
        "".join([
            "folders_to_organise:\n",
            "    - D:\\test\\data\n",
            "    - E:\\some\\folder\n",
            "\n",
            "media_extensions:\n",
            "    - .jpg\n",
            "    - .png\n"
        ])
    )

    create_test_file(fs, config_file)
    config, valid, error_msg = read_config_file(config_file.path)

    assert valid
    assert config["folders_to_organise"][0] == "D:\\test\\data"
    assert config["folders_to_organise"][1] == "E:\\some\\folder"
    assert config["media_extensions"][0] == ".jpg"
    assert config["media_extensions"][1] == ".png"