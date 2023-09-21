import os
import pytest
import shutil
from organise_media import get_media_files, safe_move

@pytest.fixture
def setup_test_environment():
    # Create a temporary test directory structure for testing
    test_dir = "test_dir"
    os.mkdir(test_dir)
    yield test_dir
    shutil.rmtree(test_dir)

def test_get_media_files_returns_zero_files_for_invalid_path(setup_test_environment):
    test_path = "./non_existant_dir/"
    result = list(get_media_files(test_path, []))

    assert len(result) == 0

def test_get_media_files_returns_zero_files_for_empty_media_types_array(setup_test_environment):
    test_path = "./test_dir/"
    result = list(get_media_files(test_path, []))

    assert len(result) == 0

def test_get_media_files_ignores_directories(setup_test_environment):
    test_path = "./test_dir/"
    subdir_path = "./test_dir/subdir/"

    media_types = [".jpg"]
    jpg_file = "./test_dir/file.jpg"

    create_test_folders_and_file_from_path(jpg_file)
    create_test_folders_and_file_from_path(subdir_path)

    assert os.path.exists(jpg_file)
    assert os.path.exists(subdir_path)

    result = list(get_media_files(test_path, media_types))

    assert len(result) == 1
    assert result[0] == "file.jpg"

def test_get_media_files_returns_files_matching_media_types_array(setup_test_environment):
    test_path = "./test_dir/"
    media_types = [".jpg", ".png"]

    jpg_file1 = "./test_dir/file1.jpg"
    jpg_file2 = "./test_dir/file2.jpg"
    png_file1 = "./test_dir/file1.png"
    png_file2 = "./test_dir/file2.png"
    mp4_file1 = "./test_dir/file1.mp4"
    mp4_file2 = "./test_dir/file2.mp4"

    create_test_folders_and_file_from_path(jpg_file1)
    create_test_folders_and_file_from_path(jpg_file2)
    create_test_folders_and_file_from_path(png_file1)
    create_test_folders_and_file_from_path(png_file2)
    create_test_folders_and_file_from_path(mp4_file1)
    create_test_folders_and_file_from_path(mp4_file2)

    assert os.path.exists(jpg_file1)
    assert os.path.exists(jpg_file2)
    assert os.path.exists(png_file1)
    assert os.path.exists(png_file2)
    assert os.path.exists(mp4_file1)
    assert os.path.exists(mp4_file2)

    result = list(get_media_files(test_path, media_types))

    assert len(result) == 4
    assert result[0] == "file1.jpg"
    assert result[1] == "file1.png"
    assert result[2] == "file2.jpg"
    assert result[3] == "file2.png"

def test_safe_move_to_existing_dir(setup_test_environment):
    src_file_path = "./test_dir/source/file.jpg"
    dest_dir_path = "./test_dir/destination/"
    expected_file_path = "./test_dir/destination/file.jpg"

    create_test_folders_and_file_from_path(src_file_path)
    create_test_folders_and_file_from_path(dest_dir_path)

    assert os.path.exists(src_file_path)
    assert os.path.exists(dest_dir_path)

    safe_move(src_file_path, dest_dir_path)
    assert not os.path.exists(src_file_path)
    assert os.path.exists(expected_file_path)

def test_safe_move_doesnt_overwrite_existing_files(setup_test_environment):
    src_file_path = "./test_dir/source/file.jpg"
    dest_dir_path = "./test_dir/destination/"
    existing_file_path = "./test_dir/destination/file.jpg"
    existing_copy_file_path = "./test_dir/destination/file_copy.jpg"
    expected_file_path = "./test_dir/destination/file_copy_copy.jpg"

    create_test_folders_and_file_from_path(src_file_path)
    create_test_folders_and_file_from_path(existing_file_path)
    create_test_folders_and_file_from_path(existing_copy_file_path)

    assert os.path.exists(src_file_path)
    assert os.path.exists(existing_file_path)
    assert os.path.exists(existing_copy_file_path)

    safe_move(src_file_path, dest_dir_path)
    assert not os.path.exists(src_file_path)
    assert os.path.exists(existing_file_path)
    assert os.path.exists(existing_copy_file_path)
    assert os.path.exists(expected_file_path)

# Helper functions
def create_test_folders_and_file_from_path(path):
    path_dirs, file_name = os.path.split(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if file_name != '':
        open(path, "x")