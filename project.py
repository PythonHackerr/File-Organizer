import argparse
from hashlib import md5
import json
from pathlib import Path
from collections import defaultdict


DEFAULT_CONFIG_FILE = {
    'temporary files': ['.tmp'],
    'invalid symbols': [':', '"', ':', '*', '?', '$', '#', "^"],
    'permissions': '644',
    'character to replace with': '_'
}

def delete_file(file):
    file.unlink()
    print(f"removed file {file}")


def get_all_files_in_dir(dir):
    return [f for f in dir.glob("**/*") if f.is_file()]


def find_same_content_files(dirs):
    files = [f for d in dirs for f in get_all_files_in_dir(d)]
    checksums = defaultdict(list)
    for f in files:
        checksums[md5(f.read_bytes()).hexdigest()].append(f)
    return [group for group in checksums.values() if len(group) > 1]


def find_inproper_permissions(dir, acceptable_perms):
    for f in get_all_files_in_dir(dir):
        if oct(f.stat().st_mode & 0o777) != acceptable_perms:
            yield f


def find_same_name(dirs):
    files = []
    for d in dirs:
        files.extend(get_all_files_in_dir(d))

    files_by_name = defaultdict(list)
    for f in files:
        files_by_name[f.name].append(f)

    return [files for files in files_by_name.values() if len(files) > 1]


def find_with_symbols(dir, symbols):
    for f in get_all_files_in_dir(dir):
        for s in symbols:
            if s in f.name:
                yield f


def find_temporary(dir, postfixes):
    for f in get_all_files_in_dir(dir):
        if f.name.endswith(tuple(postfixes)):
            yield f


def delete_same_content_files(dirs):
    file_groups = find_same_content_files(dirs)
    for files in file_groups:
        oldest = sorted(files, key=lambda f: f.stat().st_mtime)[0]
        for f in files:
            if f != oldest:
                delete_file(f)


def delete_same_naming_files(dirs):
    file_groups = find_same_name(dirs)
    for files in file_groups:
        newest = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
        for f in files:
            if f != newest:
                delete_file(f)


def change_file_permissions(dirs, usual):
    for d in dirs:
        for file in find_inproper_permissions(d, usual):
            file.chmod(usual)


def change_naming(dirs, symbols, to_replace_with):
    def get_invalid_name(file, separator):
        i = 1
        new_file = file.parent / f"{file.stem}{separator}{i}{file.suffix}"
        while new_file.exists():
            i += 1
            new_file = file.parent / f"{file.stem}{separator}{i}{file.suffix}"
        return new_file

    def replace_symbols(file, symbols, replacement):
        new_name = ''.join([replacement if c in symbols else c for c in file.name])
        return file.parent / new_name

    for d in dirs:
        for f in find_with_symbols(d, symbols):
            new_file = get_invalid_name(replace_symbols(f, symbols, to_replace_with), to_replace_with)
            new_file.parent.mkdir(parents=True, exist_ok=True)
            f.rename(new_file)


def delete_temp_files(dirs, postfixes):
    for d in dirs:
        for f in find_temporary(d, postfixes):
            delete_file(f)


def delete_empty_files(dirs):
    for d in dirs:
        for f in (file for file in get_all_files_in_dir(d) if file.stat().st_size == 0):
            delete_file(f)


def add_argument(parser, flag, help_text, **kwargs):
    parser.add_argument(flag, help=help_text, **kwargs)


# python project.py -d X -sc y -sn y -sym y -emp y -perm y -tmp y
def main():
    parser = argparse.ArgumentParser(description="Directories manager project")

    add_argument(parser, "-d","dirrectory to manage", required=True)
    add_argument(parser, "-d2", "additional directory to manage")
    add_argument(parser, "-cfg", "path to custom config file", default="", type=Path)
    add_argument(parser, "-sc", "find files with same content", nargs='?', default='n', choices=('y', 'n'))
    add_argument(parser, "-sn", "find files with same name", nargs='?', default='n', choices=('y', 'n'))
    add_argument(parser, "-sym", "find files with invalid naming", nargs='?', default='n', choices=('y', 'n'))
    add_argument(parser, "-emp", "find empty files", nargs='?', default='n', choices=('y', 'n'))
    add_argument(parser, "-perm", "find files with different access permissions", nargs='?', default='n', choices=('y', 'n'))
    add_argument(parser, "-tmp", "find temporary files", nargs='?', default='n', choices=('y', 'n'))

    args = parser.parse_args()

    main_directory = Path(args.d)
    additional_directories = [Path(directory) for directory in args.d2] if args.d2 else []
    directories = [main_directory, *additional_directories]

    cfg = DEFAULT_CONFIG_FILE
    try:
        if args.cfg.exists():
            with open(args.cfg) as config_file:
                cfg.update(json.load(config_file))
    except:
        pass

    permissions = int(cfg["permissions"], base=8)

    if args.sc == "y":
        delete_same_content_files(directories)
    if args.sn== "y":
        delete_same_naming_files(directories)
    if args.sym== "y":
        change_naming(directories, cfg["invalid symbols"], cfg["character to replace with"])
    if args.emp== "y":
        delete_empty_files(directories)
    if args.perm== "y":
        change_file_permissions(directories, permissions)
    if args.tmp== "y":
        delete_temp_files(directories, cfg["temporary files"])


if __name__ == '__main__':
    main()
