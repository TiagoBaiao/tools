import datetime
import os
import yaml
from freezegun import freeze_time
from ..organise_media import is_valid_config, read_config_file, get_media_files, safe_move, organise_media, handle_prompt_answer

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
    assert error_msg == 'Missing configuration file "config.yaml" in the same directory as "organise_media.py". Script aborted.'

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

def test_get_media_files_returns_zero_files_for_invalid_path():
    test_dir_path = "./non_existant_dir/"
    media_types = []

    result = list(get_media_files(test_dir_path, media_types))

    assert len(result) == 0

def test_get_media_files_returns_zero_files_for_empty_media_types_array(fs):
    test_dir_path = "./test_dir/"
    media_types = []

    create_test_dir(fs, test_dir_path)
    result = list(get_media_files(test_dir_path, media_types))

    assert len(result) == 0

def test_get_media_files_ignores_directories(fs):
    test_dir_path = "./test_dir/"
    test_subdir_path = "./test_dir/subdir/"
    media_types = [".jpg"]

    jpg_file = FakeFile("./test_dir/file.jpg")

    create_test_dir(fs, test_subdir_path)
    create_test_file(fs, jpg_file)

    result = list(get_media_files(test_dir_path, media_types))

    assert len(result) == 1
    assert result[0] == "file.jpg"

def test_get_media_files_returns_files_matching_media_types_array(fs):
    test_dir_path = "./test_dir/"
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/file1.jpg"),
        FakeFile("./test_dir/file2.jpg"),
        FakeFile("./test_dir/file1.png"),
        FakeFile("./test_dir/file2.png"),
        FakeFile("./test_dir/file1.mp4"),
        FakeFile("./test_dir/file2.mp4")
    ]

    create_test_files(fs, test_files)
    result = list(get_media_files(test_dir_path, media_types))

    assert len(result) == 4
    assert result[0] == "file1.jpg"
    assert result[1] == "file2.jpg"
    assert result[2] == "file1.png"
    assert result[3] == "file2.png"

def test_safe_move_to_existing_dir(fs):
    src_file = FakeFile("./test_dir/source/file.jpg", "JPG File")

    dest_dir_path = "./test_dir/destination/"
    expected_file_path = "./test_dir/destination/file.jpg"

    create_test_dir(fs, dest_dir_path)
    create_test_file(fs, src_file)

    safe_move(src_file.path, dest_dir_path)

    assert not fs.exists(src_file.path)
    assert_file_exists_with_content(fs, expected_file_path, "JPG File")

def test_safe_move_doesnt_overwrite_existing_files(fs):
    file_to_move = FakeFile("./test_dir/source/file.jpg", "JPG File")
    dest_dir_path = "./test_dir/destination/"

    test_files = [
        file_to_move,
        FakeFile("./test_dir/destination/file.jpg", "Existing JPG File"),
        FakeFile("./test_dir/destination/file_copy.jpg", "Existing JPG File Copy")
    ]

    create_test_files(fs, test_files)
    safe_move(file_to_move.path, dest_dir_path)

    assert not fs.exists(file_to_move.path)
    assert_file_exists_with_content(fs, "./test_dir/destination/file.jpg", "Existing JPG File")
    assert_file_exists_with_content(fs, "./test_dir/destination/file_copy.jpg", "Existing JPG File Copy")
    assert_file_exists_with_content(fs, "./test_dir/destination/file_copy_copy.jpg", "JPG File")

def test_organise_media_moves_zero_files_for_non_existant_directory(fs):
    dir_to_organise = "./non_existant_dir/"
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/dir_to_organise/file1.png"),
        FakeFile("./test_dir/dir_to_organise/file2.png"),
        FakeFile("./test_dir/dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    organise_media(dir_to_organise, media_types)

    for test_file in test_files:
        assert fs.exists(test_file.path)

def test_organise_media_moves_zero_files_for_empty_media_types(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = []

    test_files = [
        FakeFile("./test_dir/dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/dir_to_organise/file1.png"),
        FakeFile("./test_dir/dir_to_organise/file2.png"),
        FakeFile("./test_dir/dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    organise_media(dir_to_organise, media_types)

    assert len(os.listdir(dir_to_organise)) == 6
    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

def test_organise_media_moves_zero_files_when_no_files_with_input_media_types(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".raw"]

    test_files = [
        FakeFile("./test_dir/dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/dir_to_organise/file1.png"),
        FakeFile("./test_dir/dir_to_organise/file2.png"),
        FakeFile("./test_dir/dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    organise_media(dir_to_organise, media_types)

    assert len(os.listdir(dir_to_organise)) == 6
    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

def test_organise_media_moves_files_with_input_media_types(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/dir_to_organise/file1.jpg", "JPG File 1", datetime.datetime(2009, 10, 5)),
        FakeFile("./test_dir/dir_to_organise/file2.jpg", "JPG File 2", datetime.datetime(2013, 7, 10)),
        FakeFile("./test_dir/dir_to_organise/file1.png", "PNG File 1", datetime.datetime(2009, 10, 5)),
        FakeFile("./test_dir/dir_to_organise/file2.png", "PNG File 2", datetime.datetime(2013, 10, 5)),
        FakeFile("./test_dir/dir_to_organise/file1.mp4", "MP4 File 1", datetime.datetime(2009, 10, 5)),
        FakeFile("./test_dir/dir_to_organise/file2.mp4", "MP4 File 2", datetime.datetime(2013, 10, 5))
    ]

    create_test_files(fs, test_files)
    organise_media(dir_to_organise, media_types)

    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2009/10_October/file1.jpg", "JPG File 1")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2013/07_July/file2.jpg", "JPG File 2")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2009/10_October/file1.png", "PNG File 1")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2013/10_October/file2.png", "PNG File 2")

def test_organise_media_moves_zero_files_in_other_directories(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".jpg", ".png"]

    other_dir = "./test_dir/other_dir/"
    other_subdir = "./test_dir/dir_to_organise/other_subdir/"

    test_file_paths = [
        FakeFile("./test_dir/dir_to_organise/file1.jpg", "JPG File 1"),
        FakeFile("./test_dir/dir_to_organise/file2.jpg", "JPG File 2"),
        FakeFile("./test_dir/dir_to_organise/file1.png", "PNG File 1"),
        FakeFile("./test_dir/dir_to_organise/file2.png", "PNG File 2"),
        FakeFile("./test_dir/dir_to_organise/file1.mp4", "MP4 File 1"),
        FakeFile("./test_dir/dir_to_organise/file2.mp4", "MP4 File 2"),
        FakeFile("./test_dir/other_dir/file3.jpg", "Other JPG File 3"),
        FakeFile("./test_dir/other_dir/file3.png", "Other PNG File 3"),
        FakeFile("./test_dir/dir_to_organise/other_subdir/file4.jpg", "Other JPG File 4"),
        FakeFile("./test_dir/dir_to_organise/other_subdir/file4.png", "Other PNG File 4")
    ]

    create_test_files(fs, test_file_paths)

    assert len(os.listdir(other_dir)) == 2
    assert_file_exists_with_content(fs, "./test_dir/other_dir/file3.jpg", "Other JPG File 3")
    assert_file_exists_with_content(fs, "./test_dir/other_dir/file3.png", "Other PNG File 3")

    assert len(os.listdir(other_subdir)) == 2
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/other_subdir/file4.jpg", "Other JPG File 4")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/other_subdir/file4.png", "Other PNG File 4")

    organise_media(dir_to_organise, media_types)

    assert len(os.listdir(other_dir)) == 2
    assert_file_exists_with_content(fs, "./test_dir/other_dir/file3.jpg", "Other JPG File 3")
    assert_file_exists_with_content(fs, "./test_dir/other_dir/file3.png", "Other PNG File 3")

    assert len(os.listdir(other_subdir)) == 2
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/other_subdir/file4.jpg", "Other JPG File 4")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/other_subdir/file4.png", "Other PNG File 4")

def test_organise_media_moves_files_without_overwriting_existing_ones(fs):
    dir_to_organise = "./test_dir/dir_to_organise/"
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/dir_to_organise/file1.jpg", "JPG File 1", datetime.datetime(2009, 10, 5)),
        FakeFile("./test_dir/dir_to_organise/2009/10_October/file2.jpg", "Existing JPG File 2", datetime.datetime(2009, 10, 5)),
        FakeFile("./test_dir/dir_to_organise/file3.jpg", "JPG File 3", datetime.datetime(2010, 7, 5)),
        FakeFile("./test_dir/dir_to_organise/2010/07_July/file3.jpg", "Existing JPG File 3", datetime.datetime(2010, 7, 5)),
        FakeFile("./test_dir/dir_to_organise/file4.png", "PNG File 4", datetime.datetime(2011, 5, 5)),
        FakeFile("./test_dir/dir_to_organise/2011/05_May/file4.png", "Existing PNG File 4", datetime.datetime(2011, 5, 5)),
        FakeFile("./test_dir/dir_to_organise/2011/05_May/file4_copy.png", "Existing PNG File 4 Copy", datetime.datetime(2011, 5, 5))
    ]

    create_test_files(fs, test_files)
    organise_media(dir_to_organise, media_types)

    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2009/10_October/file1.jpg", "JPG File 1")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2009/10_October/file2.jpg", "Existing JPG File 2")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2010/07_July/file3.jpg", "Existing JPG File 3")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2010/07_July/file3_copy.jpg", "JPG File 3")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2011/05_May/file4.png", "Existing PNG File 4")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2011/05_May/file4_copy.png", "Existing PNG File 4 Copy")
    assert_file_exists_with_content(fs, "./test_dir/dir_to_organise/2011/05_May/file4_copy_copy.png", "PNG File 4")

def test_script_moves_zero_files_when_prompt_answer_is_not_yes(fs):
    prompt_answer = "no"
    dirs_to_organise = [
        "./test_dir/first_dir_to_organise/",
        "./test_dir/second_dir_to_organise/"
    ]
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/first_dir_to_organise/file1.png"),
        FakeFile("./test_dir/second_dir_to_organise/file2.png"),
        FakeFile("./test_dir/first_dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/second_dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    for test_file in test_files:
        assert fs.exists(test_file.path)

def test_script_moves_zero_files_when_supplied_dirs_do_not_exist(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./non_existant_dir1/",
        "./non_existant_dir2/"
    ]
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/first_dir_to_organise/file1.png"),
        FakeFile("./test_dir/second_dir_to_organise/file2.png"),
        FakeFile("./test_dir/first_dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/second_dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    for test_file in test_files:
        assert fs.exists(test_file.path)

def test_script_moves_zero_files_when_no_dirs_supplied(fs):
    prompt_answer = "yes"
    dirs_to_organise = []
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/first_dir_to_organise/file1.png"),
        FakeFile("./test_dir/second_dir_to_organise/file2.png"),
        FakeFile("./test_dir/first_dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/second_dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    for test_file in test_files:
        assert fs.exists(test_file.path)

def test_script_moves_zero_files_when_no_media_types_supplied(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./test_dir/first_dir_to_organise/",
        "./test_dir/second_dir_to_organise/"
    ]
    media_types = []

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/first_dir_to_organise/file1.png"),
        FakeFile("./test_dir/second_dir_to_organise/file2.png"),
        FakeFile("./test_dir/first_dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/second_dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

def test_script_moves_zero_files_when_supplied_dirs_do_not_have_files_matching_media_types(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./test_dir/first_dir_to_organise/",
        "./test_dir/second_dir_to_organise/"
    ]
    media_types = [".raw", ".bmp"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg"),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg"),
        FakeFile("./test_dir/first_dir_to_organise/file1.png"),
        FakeFile("./test_dir/second_dir_to_organise/file2.png"),
        FakeFile("./test_dir/first_dir_to_organise/file1.mp4"),
        FakeFile("./test_dir/second_dir_to_organise/file2.mp4")
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

def test_script_only_moves_files_matching_media_types(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./test_dir/first_dir_to_organise/",
        "./test_dir/second_dir_to_organise/"
    ]
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg", "JPG File 1", datetime.datetime(2009, 9, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg", "JPG File 2", datetime.datetime(2010, 3, 5)),
        FakeFile("./test_dir/first_dir_to_organise/file1.png", "PNG File 1", datetime.datetime(2011, 6, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.png", "PNG File 2", datetime.datetime(2012, 8, 5)),
        FakeFile("./test_dir/first_dir_to_organise/file1.mp4", "MP4 File 1", datetime.datetime(2013, 1, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.mp4", "MP4 File 1", datetime.datetime(2014, 11, 5))
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2009/09_September/file1.jpg", "JPG File 1")
    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2011/06_June/file1.png", "PNG File 1")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/2010/03_March/file2.jpg", "JPG File 2")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/2012/08_August/file2.png", "PNG File 2")

def test_script_moves_files_for_existing_dirs_and_ignores_non_existant_dirs(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./non_existant_dir/",
        "./test_dir/first_dir_to_organise/"
    ]
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg", "JPG File 1", datetime.datetime(2009, 9, 5)),
        FakeFile("./test_dir/first_dir_to_organise/file1.png", "PNG File 1", datetime.datetime(2011, 6, 5))
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types)

    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2009/09_September/file1.jpg", "JPG File 1")
    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2011/06_June/file1.png", "PNG File 1")

def test_script_does_not_move_files_in_other_dirs(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./test_dir/first_dir_to_organise/",
        "./test_dir/second_dir_to_organise/"
    ]
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg", "JPG File 1", datetime.datetime(2009, 9, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg", "JPG File 2", datetime.datetime(2010, 3, 5)),
        FakeFile("./test_dir/first_dir_to_organise/file1.png", "PNG File 1", datetime.datetime(2011, 6, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.png", "PNG File 2", datetime.datetime(2012, 8, 5)),
        FakeFile("./test_dir/other_dir/file3.jpg", "Other JPG File 3", datetime.datetime(2013, 1, 5)),
        FakeFile("./test_dir/first_dir_to_organise/other_subdir/file4.jpg", "Other JPG File 4", datetime.datetime(2014, 11, 5)),
        FakeFile("./test_dir/second_dir_to_organise/other_subdir/file3.png", "Other PNG File 3", datetime.datetime(2015, 12, 5))
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    assert not fs.exists("./test_dir/first_dir_to_organise/file1.jpg")
    assert not fs.exists("./test_dir/second_dir_to_organise/file2.jpg")
    assert not fs.exists("./test_dir/first_dir_to_organise/file1.png")
    assert not fs.exists("./test_dir/second_dir_to_organise/file2.png")
    assert_file_exists_with_content(fs, "./test_dir/other_dir/file3.jpg", "Other JPG File 3")
    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/other_subdir/file4.jpg", "Other JPG File 4")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/other_subdir/file3.png", "Other PNG File 3")

def test_script_does_not_overwrite_existing_files(fs):
    prompt_answer = "yes"
    dirs_to_organise = [
        "./test_dir/first_dir_to_organise/",
        "./test_dir/second_dir_to_organise/"
    ]
    media_types = [".jpg", ".png"]

    test_files = [
        FakeFile("./test_dir/first_dir_to_organise/file1.jpg", "JPG File 1", datetime.datetime(2009, 9, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.jpg", "JPG File 2", datetime.datetime(2010, 3, 5)),
        FakeFile("./test_dir/first_dir_to_organise/file1.png", "PNG File 1", datetime.datetime(2009, 9, 5)),
        FakeFile("./test_dir/second_dir_to_organise/file2.png", "PNG File 2", datetime.datetime(2010, 3, 5)),
        FakeFile("./test_dir/first_dir_to_organise/2009/09_September/file1.jpg", "Existing JPG File 1", datetime.datetime(2009, 9, 5)),
        FakeFile("./test_dir/second_dir_to_organise/2010/03_March/file2.png", "Existing PNG File 2", datetime.datetime(2010, 3, 5)),
        FakeFile("./test_dir/second_dir_to_organise/2010/03_March/file2_copy.png", "Existing PNG File 2 Copy", datetime.datetime(2010, 3, 5))
    ]

    create_test_files(fs, test_files)
    handle_prompt_answer(prompt_answer, dirs_to_organise, media_types)

    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2009/09_September/file1.jpg", "Existing JPG File 1")
    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2009/09_September/file1_copy.jpg", "JPG File 1")
    assert_file_exists_with_content(fs, "./test_dir/first_dir_to_organise/2009/09_September/file1.png", "PNG File 1")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/2010/03_March/file2.jpg", "JPG File 2")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/2010/03_March/file2.png", "Existing PNG File 2")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/2010/03_March/file2_copy.png", "Existing PNG File 2 Copy")
    assert_file_exists_with_content(fs, "./test_dir/second_dir_to_organise/2010/03_March/file2_copy_copy.png", "PNG File 2")

# Helper functions
def create_test_dir(fs, path):
    if not fs.exists(os.path.dirname(path)):
        fs.create_dir(os.path.dirname(path))

    assert fs.exists(os.path.dirname(path))

def create_test_file(fs, file):
    create_test_dir(fs, file.path)

    with freeze_time(file.creation_date):
        fs.create_file(file.path, contents = file.content)
        assert fs.exists(file.path)

def create_test_files(fs, files):
    for file in files:
        create_test_file(fs, file)

def assert_file_exists_with_content(fs, file_path, expected_content):
    assert fs.exists(file_path)

    with open(file_path, "r") as file:
        assert file.read() == expected_content

def assert_only_moved_files_with_extension_in_media_types(fs, test_files, media_types):
    for test_file in test_files:
        filename, file_extension = os.path.splitext(test_file.path)
        if file_extension in media_types:
            assert not fs.exists(test_file.path)
        else:
            assert fs.exists(test_file.path)

class FakeFile:
    def __init__(self, path = "", content = None, creation_date = datetime.datetime.now()):
        self.path = path
        self.content = content
        self.creation_date = creation_date
