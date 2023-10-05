import datetime
from organise_media.organise_media.user_prompt import handle_prompt_answer
from organise_media.tests.test_helpers import FakeFile, create_test_files, assert_file_exists_with_content, assert_only_moved_files_with_extension_in_media_types

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
