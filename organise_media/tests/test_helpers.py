import datetime
import os
from freezegun import freeze_time

class FakeFile:
    def __init__(self, path = "", content = None, creation_date = datetime.datetime.now()):
        self.path = path
        self.content = content
        self.creation_date = creation_date

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
