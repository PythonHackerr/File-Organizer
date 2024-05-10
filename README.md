# File Organizer

The project.py script is a tool for organizing a set of files into a specific root directory and additional directories. It allows you to identify and manage duplicates, temporary files, files with incorrect names, empty files and allows you to change file permissions.

### Functions:
* Duplicate Removal: Removes duplicate files, leaving only the oldest file based on modification date.
* Temporary file management: Deletes temporary files based on defined file extensions.
* File Rename: Renames files that contain invalid symbols, replacing them with a defined "_" substitute.
* Change Permissions: Allows you to change the permissions of files in a directory to defined permissions.
* Managing files with the same names: For files with the same names, the script leaves the latest version.

### Use:
The script runs from the command line, offering various options, each with a choice of 'y' (yes) or 'n' (no):

-d: Root directory to manage (required).
-d2: Additional directory to manage.
-cfg: Path to the custom configuration file.
-sc: Option to find files with the same content.
-sn: Option to find files with the same name.
-sym: Option to find files with invalid names.
-emp: Option to find empty files.
-perm: Option to check file permissions.
-tmp: Option to find temporary files.

### Example of use:
Running the script for the root directory X and the additional directory X2, with the option to remove duplicates and change file permissions:

> python project.py -d X -d2 X2 -sc y -perm y
> python project.py -d X -sc y -sn y -sym y -emp y -perm y -tmp y

### Requirements:
The script requires Python version 3 with the argparse, hashlib, json, datetime, pathlib, and collections modules installed.
