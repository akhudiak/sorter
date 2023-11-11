import os
from pathlib import Path
import re
import shutil
import sys

from exceptions import TooManyWordsError, UnchoosedDirectoryError


files_suffixes = {
    "archives": [".zip", ".gz", ".tar"],
    "video": [".avi", ".mp4", ".mov", ".mkv"],
    "audio": [".mp3", ".ogg", ".wav", ".amr"],
    "documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "images": [".jpeg", ".png", ".jpg", ".svg"],
    "unknown": []
}


def error_handler(func):
    def wrapper(*args):
        try:
            return func(*args)
        except (TooManyWordsError, UnchoosedDirectoryError) as error:
            print(error)
            sys.exit()
    return wrapper


def create_folders(parent_folder, new_folders):

    new_folders_path = {}

    for new_folder in new_folders:

        new_folder_path = parent_folder / new_folder
        new_folder_path.mkdir()
        new_folders_path[new_folder] = new_folder_path

    return new_folders_path


def move_file(file, files_suffixes, new_folders_path):

    for key in files_suffixes:

        if file.suffix in files_suffixes[key]:
            return key, Path(shutil.move(file, new_folders_path[key])), True

    return "unknown", Path(shutil.move(file, new_folders_path["unknown"])), False


def normalize(name):

    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

    TRANS = {}
        
    for i, j in zip(CYRILLIC_SYMBOLS, TRANSLATION):

        TRANS[ord(i)] = j
        TRANS[ord(i.upper())] = j.upper()

    trans_name = name.translate(TRANS)

    name = re.sub("\W", "_", trans_name)

    return name


def print_result(result_lists):

    for key in result_lists:

        print(key.upper())

        for val in result_lists[key]:
            print(val)

        print("-" * 30)


def sorter(sortable_folder, files_suffixes, new_folders_path, result_lists):

    items = sortable_folder.iterdir()

    for item in items:

        if item.is_file():

            key, file, file_ext = move_file(item, files_suffixes, new_folders_path)

            renamed_file = f"{file.parent / normalize(file.stem)}{file.suffix}"
            file = file.rename(renamed_file)

            try:
                result_lists[key].append(file.name)
            except KeyError:
                result_lists[key] = file.name

            if file_ext:
                result_lists["known extension"].add(item.suffix)
            else:
                result_lists["unknown extension"].add(item.suffix)

        elif item not in new_folders_path.values():

            result_lists = sorter(item, files_suffixes, new_folders_path, result_lists)
            item.rmdir()

    return result_lists


def unpacking(archives_path):

    for item in archives_path.iterdir():
        
        shutil.unpack_archive(item, item.parent / item.stem)
        os.remove(item)


@error_handler
def get_sortable_folder() -> Path:

    if len(sys.argv) > 2:
        raise TooManyWordsError
    elif len(sys.argv) < 2:
        raise UnchoosedDirectoryError

    sortable_folder = Path(sys.argv[1])

    return sortable_folder


def create_folder_copy(folder: Path) -> Path:
    
    parent: Path = folder.parent
    dst: Path = parent / (folder.stem + "_copy")

    if dst.exists():
        shutil.rmtree(dst)
    
    copy: Path = shutil.copytree(folder, dst)
    
    return copy
    

def main():

    sortable_folder = get_sortable_folder()
    sortable_folder_copy = create_folder_copy(sortable_folder)

    new_folders_path = create_folders(sortable_folder_copy, files_suffixes.keys())

    result_lists = {
        "known extension": set(),
        "unknown extension": set()
    }

    for key in files_suffixes:
        result_lists[key] = []

    result_lists = sorter(sortable_folder_copy, files_suffixes, new_folders_path, result_lists)
    
    print_result(result_lists)

    unpacking(new_folders_path["archives"])


if __name__ == "__main__":
    main()
