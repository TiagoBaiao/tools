# Organise Media

Organise files contained in a list of directories in `year/month/` sub-directories according to each file's creation date.

## Motivation

The motivation for this project was born out of a desire to keep folders with a massive amount of photos in an external hard drive organised in some way, to make it easier to find specific files. The scope of the project later evolved to enable organising other types of files by configuring which file extensions to handle.

## Requirements

Install [python](https://www.python.org/downloads/).

Python version 3.4+ includes `pip` by default. If you are using an earlier version of python you may need to [install pip](https://pip.pypa.io/en/stable/installation/).

Run the following command to install dependencies:

    $ pip install -r requirements.txt

## Usage

The `organise_media` script is fairly straightforward to use. Start by configuring which directories to organise and which file extensions to handle, and then just run the script.

### Configuration

Before running the `organise_media` script make sure that a `config.yaml` file exists in the root directory of the project. It must have the following configuration variables:

 - **folders_to_organise**: a list of directories where the script will look for files to organise in sub-directories
 - **media_extensions**: a list of file extensions which the script will use to mark files as eligible for organisation

An example of a valid configuration to run the script is:
```yaml
folders_to_organise:
    - C:\example_A\example1\example2\example3
    - C:\example_B\example1\example2\example3

media_extensions:
    - .jpg
    - .jpeg
    - .png
    - .mp4
```
**Note**: the dot (.) for each media_extensions list item is important!

If the configuration is not valid, either because the configuration file is missing, is blank, or does not declare the expected configuration variables as lists, the script will abort execution with an error message.

### Run

    $ python run_organise_media.py

### Output

After running the script, the configured directories to organise, that exist and had files eligible to be organised, should have those files moved to `year/month/` sub-directories within them, according to the files' creation_date.

For better accessibility, when using a file explorer that displays folders ordered alphabetically, the month folder names are prefixed with their respective ordinal number, e.g. `01_January, 02_February, etc...`

As an example, if we start with a folder structure that looks like this:

```
.
├── dir1
│   ├── file_01_11_2019.png
│   ├── file_15_12_2019.png
│   └── file_12_02_2022.png
├── dir2
│   ├── file_04_05_2020.png
│   ├── file_18_05_2021.png
│   └── file_20_07_2021.png
├── dir3
├── file_in_root.png
```

And we configure the script to organise `.png` files in `dir1` and `dir2`, we end up with the following tree structure after running the script:

```
.
├── dir1
│   ├── 2019
│      ├── 11_November
│         └── file_01_11_2019.png
│      └── 12_December
│         └── file_15_12_2019.png
│   └── 2022
│      └── 02_February
│         └── file_12_02_2022.png
├── dir2
│   ├── 2020
│      └── 05_May
│         └── file_04_05_2020.png
│   └── 2021
│      ├── 05_May
│         └── file_18_05_2021.png
│      └── 07_July
│         └── file_20_07_2021.png
├── dir3
├── file_in_root.png
```

Filename clashes when trying to move a file are resolved by appending `_copy` to the filename before the extension. No files are overwritten in the process.

As an example, if we start with a folder structure that looks like this:

```
.
├── dir1
│   ├── file_01_11_2019.png
│   ├── 2019
│      ├── 11_November
│         └── file_01_11_2019.png
├── dir2
│   ├── file_04_05_2020.png
│   ├── 2020
│      └── 05_May
│         └── file_04_05_2020.png
│         └── file_04_05_2020_copy.png
├── file_in_root.png
```

And we configure the script to organise `.png` files in `dir1` and `dir2`, we end up with the following tree structure after running the script:

```
.
├── dir1
│   ├── 2019
│      ├── 11_November
│         └── file_01_11_2019.png
│         └── file_01_11_2019_copy.png
├── dir2
│   ├── 2020
│      └── 05_May
│         └── file_04_05_2020.png
│         └── file_04_05_2020_copy.png
│         └── file_04_05_2020_copy_copy.png
├── file_in_root.png
```

### Logging

The log output can be found in the `log/` directory, generated in the root of the project, the first time the script is run. In subsequent runs, new log entries are appended to the log file.

## Testing

The project contains both unit and functional tests, which you can run using `pytest`.

### Setup

Run the following command to install dependencies (including `pytest`):

    $ pip install -r requirements/test.txt

### Run Tests

    $ pytest

### Debug Test Discoverability

    $ pytest --collect-only
