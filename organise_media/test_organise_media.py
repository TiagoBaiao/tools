import datetime
import os
import yaml
from freezegun import freeze_time
from organise_media import is_valid_config, read_config_file, get_media_files, safe_move, organise_media

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
    config_file_path = "./test_dir/config.yaml"
    config, valid, error_msg = read_config_file(config_file_path)

    assert not valid
    assert error_msg == 'Missing configuration file "config.yaml" in the same directory as "organise_media.py". Script aborted.'

def test_read_config_file_returns_false_for_empty_yaml_file(fs):
    config_file_path = "./test_dir/config.yaml"
    create_test_folders_and_file_from_path(fs, config_file_path, "".join([]))

    config, valid, error_msg = read_config_file(config_file_path)

    assert not valid
    assert error_msg == 'The file "config.yaml" must have configuration variables defined. Script aborted.'

def test_read_config_file_returns_false_for_invalid_yaml_file(fs):
    config_file_path = "./test_dir/config.yaml"
    create_test_folders_and_file_from_path(
        fs,
        config_file_path,
        "".join([
            "media_extensions:  - .jpg  - .png"
        ])
    )

    config, valid, error_msg = read_config_file(config_file_path)

    assert not valid
    assert isinstance(error_msg, yaml.YAMLError)

def test_read_config_file_returns_false_for_yaml_file_misisng_folders_to_organise(fs):
    config_file_path = "./test_dir/config.yaml"
    create_test_folders_and_file_from_path(
        fs,
        config_file_path,
        "".join([
            "media_extensions:\n",
            "    - .jpg\n",
            "    - .png\n"
        ])
    )

    config, valid, error_msg = read_config_file(config_file_path)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable folders_to_organise of type list. Script aborted.'

def test_read_config_file_returns_false_for_yaml_file_misisng_media_extensions(fs):
    config_file_path = "./test_dir/config.yaml"
    create_test_folders_and_file_from_path(
        fs,
        config_file_path,
        "".join([
            "folders_to_organise:\n",
            "    - D:\\test\\data\n",
            "    - E:\\some\\folder\n"
        ])
    )

    config, valid, error_msg = read_config_file(config_file_path)

    assert not valid
    assert error_msg == 'The configuration file "config.yaml" must have a variable media_extensions of type list. Script aborted.'

def test_read_config_file_returns_true_and_config_matching_yaml_attributes(fs):
    config_file_path = "./test_dir/config.yaml"
    create_test_folders_and_file_from_path(
        fs,
        config_file_path,
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

    config, valid, error_msg = read_config_file(config_file_path)

    assert valid
    assert config["folders_to_organise"][0] == "D:\\test\\data"
    assert config["folders_to_organise"][1] == "E:\\some\\folder"
    assert config["media_extensions"][0] == ".jpg"
    assert config["media_extensions"][1] == ".png"

def test_get_media_files_returns_zero_files_for_invalid_path():
    test_path = "./non_existant_dir/"
    result = list(get_media_files(test_path, []))

    assert len(result) == 0

def test_get_media_files_returns_zero_files_for_empty_media_types_array(fs):
    test_path = "./test_dir/"
    create_test_folders_and_file_from_path(fs, test_path)

    result = list(get_media_files(test_path, []))

    assert len(result) == 0

def test_get_media_files_ignores_directories(fs):
    test_path = "./test_dir/"
    subdir_path = "./test_dir/subdir/"

    media_types = [".jpg"]
    jpg_file = "./test_dir/file.jpg"

    create_test_folders_and_file_from_path(fs, jpg_file)
    create_test_folders_and_file_from_path(fs, subdir_path)

    assert os.path.exists(jpg_file)
    assert os.path.exists(subdir_path)

    result = list(get_media_files(test_path, media_types))

    assert len(result) == 1
    assert result[0] == "file.jpg"

def test_get_media_files_returns_files_matching_media_types_array(fs):
    test_path = "./test_dir/"
    media_types = [".jpg", ".png"]

    jpg_file1 = "./test_dir/file1.jpg"
    jpg_file2 = "./test_dir/file2.jpg"
    png_file1 = "./test_dir/file1.png"
    png_file2 = "./test_dir/file2.png"
    mp4_file1 = "./test_dir/file1.mp4"
    mp4_file2 = "./test_dir/file2.mp4"

    create_test_folders_and_file_from_path(fs, jpg_file1)
    create_test_folders_and_file_from_path(fs, jpg_file2)
    create_test_folders_and_file_from_path(fs, png_file1)
    create_test_folders_and_file_from_path(fs, png_file2)
    create_test_folders_and_file_from_path(fs, mp4_file1)
    create_test_folders_and_file_from_path(fs, mp4_file2)

    assert os.path.exists(jpg_file1)
    assert os.path.exists(jpg_file2)
    assert os.path.exists(png_file1)
    assert os.path.exists(png_file2)
    assert os.path.exists(mp4_file1)
    assert os.path.exists(mp4_file2)

    result = list(get_media_files(test_path, media_types))

    assert len(result) == 4
    assert result[0] == "file1.jpg"
    assert result[1] == "file2.jpg"
    assert result[2] == "file1.png"
    assert result[3] == "file2.png"

def test_safe_move_to_existing_dir(fs):
    src_file_path = "./test_dir/source/file.jpg"
    dest_dir_path = "./test_dir/destination/"
    expected_file_path = "./test_dir/destination/file.jpg"

    create_test_folders_and_file_from_path(fs, src_file_path)
    create_test_folders_and_file_from_path(fs, dest_dir_path)

    assert os.path.exists(src_file_path)
    assert os.path.exists(dest_dir_path)

    safe_move(src_file_path, dest_dir_path)
    assert not os.path.exists(src_file_path)
    assert os.path.exists(expected_file_path)

def test_safe_move_doesnt_overwrite_existing_files(fs):
    src_file_path = "./test_dir/source/file.jpg"
    dest_dir_path = "./test_dir/destination/"
    existing_file_path = "./test_dir/destination/file.jpg"
    existing_copy_file_path = "./test_dir/destination/file_copy.jpg"
    expected_file_path = "./test_dir/destination/file_copy_copy.jpg"

    create_test_folders_and_file_from_path(fs, src_file_path)
    create_test_folders_and_file_from_path(fs, existing_file_path)
    create_test_folders_and_file_from_path(fs, existing_copy_file_path)

    assert os.path.exists(src_file_path)
    assert os.path.exists(existing_file_path)
    assert os.path.exists(existing_copy_file_path)

    safe_move(src_file_path, dest_dir_path)
    assert not os.path.exists(src_file_path)
    assert os.path.exists(existing_file_path)
    assert os.path.exists(existing_copy_file_path)
    assert os.path.exists(expected_file_path)

def test_organise_media_moves_zero_files_for_non_existant_directory(fs):
    dir_to_organise = "./non_existant_dir/"
    media_types = [".jpg", ".png"]

    test_files = [
        { 'path': "./test_dir/dir_to_organise/file1.jpg" },
        { 'path': "./test_dir/dir_to_organise/file2.jpg" },
        { 'path': "./test_dir/dir_to_organise/file1.png" },
        { 'path': "./test_dir/dir_to_organise/file2.png" },
        { 'path': "./test_dir/dir_to_organise/file1.mp4" },
        { 'path': "./test_dir/dir_to_organise/file2.mp4" }
    ]

    create_files_for_organise_media_tests(fs, test_files)

    organise_media(dir_to_organise, media_types)

    for test_file in test_files:
        assert os.path.exists(test_file['path'])

def test_organise_media_moves_zero_files_for_empty_media_types(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = []

    test_files = [
        { 'path': "./test_dir/dir_to_organise/file1.jpg" },
        { 'path': "./test_dir/dir_to_organise/file2.jpg" },
        { 'path': "./test_dir/dir_to_organise/file1.png" },
        { 'path': "./test_dir/dir_to_organise/file2.png" },
        { 'path': "./test_dir/dir_to_organise/file1.mp4" },
        { 'path': "./test_dir/dir_to_organise/file2.mp4" }
    ]

    create_files_for_organise_media_tests(fs, test_files)

    organise_media(dir_to_organise, media_types)

    for test_file in test_files:
        assert os.path.exists(test_file['path'])

def test_organise_media_moves_zero_files_when_no_files_with_input_media_types(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".raw"]

    test_files = [
        { 'path': "./test_dir/dir_to_organise/file1.jpg" },
        { 'path': "./test_dir/dir_to_organise/file2.jpg" },
        { 'path': "./test_dir/dir_to_organise/file1.png" },
        { 'path': "./test_dir/dir_to_organise/file2.png" },
        { 'path': "./test_dir/dir_to_organise/file1.mp4" },
        { 'path': "./test_dir/dir_to_organise/file2.mp4" }
    ]

    create_files_for_organise_media_tests(fs, test_files)

    organise_media(dir_to_organise, media_types)

    for test_file in test_files:
        assert os.path.exists(test_file['path'])

def test_organise_media_moves_files_with_input_media_types(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".jpg", ".png"]

    test_files = [
        { 'path': "./test_dir/dir_to_organise/file1.jpg", 'creation_date': datetime.datetime(2009, 10, 5) },
        { 'path': "./test_dir/dir_to_organise/file2.jpg", 'creation_date': datetime.datetime(2013, 7, 10) },
        { 'path': "./test_dir/dir_to_organise/file1.png", 'creation_date': datetime.datetime(2009, 10, 5) },
        { 'path': "./test_dir/dir_to_organise/file2.png", 'creation_date': datetime.datetime(2013, 10, 5) },
        { 'path': "./test_dir/dir_to_organise/file1.mp4", 'creation_date': datetime.datetime(2009, 10, 5) },
        { 'path': "./test_dir/dir_to_organise/file2.mp4", 'creation_date': datetime.datetime(2013, 10, 5) }
    ]

    create_files_for_organise_media_tests(fs, test_files)

    organise_media(dir_to_organise, media_types)

    for test_file in test_files:
        filename, file_extension = os.path.splitext(test_file['path'])
        if file_extension in media_types:
            assert not os.path.exists(test_file['path'])
        else:
            assert os.path.exists(test_file['path'])

    assert os.path.exists("./test_dir/dir_to_organise/2009/10_October/file1.jpg")
    assert os.path.exists("./test_dir/dir_to_organise/2013/07_July/file2.jpg")
    assert os.path.exists("./test_dir/dir_to_organise/2009/10_October/file1.png")
    assert os.path.exists("./test_dir/dir_to_organise/2013/10_October/file2.png")

def test_organise_media_moves_zero_files_in_other_directories(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".jpg", ".png"]

    other_dir = "./test_dir/other_dir/"
    other_subdir = "./test_dir/dir_to_organise/other_subdir/"

    test_file_paths = [
        { 'path': "./test_dir/dir_to_organise/file1.jpg" },
        { 'path': "./test_dir/dir_to_organise/file2.jpg" },
        { 'path': "./test_dir/dir_to_organise/file1.png" },
        { 'path': "./test_dir/dir_to_organise/file2.png" },
        { 'path': "./test_dir/dir_to_organise/file1.mp4" },
        { 'path': "./test_dir/dir_to_organise/file2.mp4" },
        { 'path': "./test_dir/other_dir/file3.jpg" },
        { 'path': "./test_dir/other_dir/file3.png" },
        { 'path': "./test_dir/dir_to_organise/other_subdir/file4.jpg" },
        { 'path': "./test_dir/dir_to_organise/other_subdir/file4.png" }
    ]

    create_files_for_organise_media_tests(fs, test_file_paths)

    assert len(os.listdir(other_dir)) == 2
    assert len(os.listdir(other_subdir)) == 2

    organise_media(dir_to_organise, media_types)

    assert len(os.listdir(other_dir)) == 2
    assert len(os.listdir(other_subdir)) == 2

def test_organise_media_moves_files_without_overwriting_existing_ones(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".jpg", ".png"]

    test_files = [
        { 'path': "./test_dir/dir_to_organise/file1.jpg", 'creation_date': datetime.datetime(2009, 10, 5) },
        { 'path': "./test_dir/dir_to_organise/2009/10_October/file2.jpg", 'creation_date': datetime.datetime(2009, 10, 5) },
        { 'path': "./test_dir/dir_to_organise/file3.jpg", 'creation_date': datetime.datetime(2010, 7, 5) },
        { 'path': "./test_dir/dir_to_organise/2010/07_July/file3.jpg", 'creation_date': datetime.datetime(2010, 7, 5) },
        { 'path': "./test_dir/dir_to_organise/file4.png", 'creation_date': datetime.datetime(2011, 5, 5) },
        { 'path': "./test_dir/dir_to_organise/2011/05_May/file4.png", 'creation_date': datetime.datetime(2011, 5, 5) },
        { 'path': "./test_dir/dir_to_organise/2011/05_May/file4_copy.png", 'creation_date': datetime.datetime(2011, 5, 5) }
    ]

    create_files_for_organise_media_tests(fs, test_files)

    organise_media(dir_to_organise, media_types)

    assert os.path.exists("./test_dir/dir_to_organise/2009/10_October/file1.jpg")
    assert os.path.exists("./test_dir/dir_to_organise/2009/10_October/file2.jpg")
    assert os.path.exists("./test_dir/dir_to_organise/2010/07_July/file3.jpg")
    assert os.path.exists("./test_dir/dir_to_organise/2010/07_July/file3_copy.jpg")
    assert os.path.exists("./test_dir/dir_to_organise/2011/05_May/file4.png")
    assert os.path.exists("./test_dir/dir_to_organise/2011/05_May/file4_copy.png")
    assert os.path.exists("./test_dir/dir_to_organise/2011/05_May/file4_copy_copy.png")

# Helper functions
def create_test_folders_and_file_from_path(fs, path, content = None, creation_date = datetime.datetime.now()):
    path_dirs, file_name = os.path.split(path)
    if not fs.exists(os.path.dirname(path)):
        fs.create_dir(os.path.dirname(path))

    if file_name != '':
        with freeze_time(creation_date):
            if content is None:
                fs.create_file(path)
            else:
                fs.create_file(path, contents = content)

def create_files_for_organise_media_tests(fs, files):
    for file in files:
        if 'creation_date' in file:
            create_test_folders_and_file_from_path(fs, file['path'], creation_date = file['creation_date'])
        else:
            create_test_folders_and_file_from_path(fs, file['path'])

        assert os.path.exists(file['path'])