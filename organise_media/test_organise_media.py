import os
import pytest
import shutil
from organise_media import safe_move

@pytest.fixture
def setup_test_environment():
    # Create a temporary test directory structure for testing
    test_dir = "test_dir"
    os.mkdir(test_dir)
    yield test_dir
    shutil.rmtree(test_dir)

def test_safe_move_to_existing_dir(setup_test_environment):
    src_path = "./test_dir/source/file.jpg"
    dest_path = "./test_dir/destination/"

    create_test_folders_and_file_from_path(src_path)
    create_test_folders_and_file_from_path(dest_path)

    assert os.path.exists(src_path)
    assert os.path.exists(dest_path)

    safe_move(src_path, dest_path)
    assert not os.path.exists(src_path)
    assert os.path.exists(dest_path)

# Helper functions
def create_test_folders_and_file_from_path(path):
    os.makedirs(os.path.dirname(path))

    path_dirs, file_name = os.path.split(path)
    if file_name != '':
        open(path, "x")