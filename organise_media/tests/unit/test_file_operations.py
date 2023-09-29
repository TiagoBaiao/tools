import datetime
import os
from organise_media.organise_media.file_operations import organise_media, get_media_files, safe_move
from organise_media.tests.test_helpers import FakeFile, create_test_dir, create_test_file, create_test_files, assert_file_exists_with_content, assert_only_moved_files_with_extension_in_media_types

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