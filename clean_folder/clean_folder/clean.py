import os
from pathlib import Path
import re
import shutil
import sys
from typing import Dict, List, Tuple

from exceptions import TooManyWordsError, UnchoosedDirectoryError


CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
            "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

def create_trans_table():

    trans_table = {}
        
    for i, j in zip(CYRILLIC_SYMBOLS, TRANSLATION):

        trans_table[ord(i)] = j
        trans_table[ord(i.upper())] = j.upper()

    return trans_table

TRANS = create_trans_table()


SUFFIXES = {
    "archives": [".zip", ".tar"],
    "video": [".avi", ".mp4", ".mov", ".mkv"],
    "audio": [".mp3", ".ogg", ".wav", ".amr"],
    "documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "images": [".jpeg", ".png", ".jpg", ".svg"],
    "unknown": []
}

destination_folders: Dict[str, Path] = {}

def create_folders(parent: Path) -> None:

    for name in SUFFIXES.keys():

        new_folder: Path = parent / name
        new_folder.mkdir()
        destination_folders[name] = new_folder


def error_handler(func):
    def wrapper(*args):
        try:
            return func(*args)
        except (TooManyWordsError, UnchoosedDirectoryError) as error:
            print(error)
            sys.exit()
    return wrapper


def move_file(file: Path) -> Tuple[str, Path]:

    for folder in SUFFIXES:

        if file.suffix in SUFFIXES[folder]:
            return folder, Path(shutil.move(file, destination_folders[folder]))

    return "unknown", Path(shutil.move(file, destination_folders["unknown"]))


def normalize(name: str) -> str:

    translated_name = name.translate(TRANS)

    formatted_name = re.sub("\W", "_", translated_name)

    return formatted_name


def print_result(result_lists: Dict[str, List[str]]) -> None:

    for key in result_lists:

        print(key.upper())

        for val in result_lists[key]:
            print(val)

        print("-" * 30)


def sorter(sortable_folder: Path) -> Dict[str, List[str]]:

    result_lists: Dict[str, List[str]] = {}

    items = [i for i in sortable_folder.rglob("*") if i.is_file()]

    for item in items:

        dst_folder, file = move_file(item)

        renamed_file = f"{file.parent / normalize(file.stem)}{file.suffix}"
        file = file.rename(renamed_file)

        try:
            result_lists[dst_folder].append(file.name)
        except KeyError:
            result_lists[dst_folder] = [file.name]

    for folder in sortable_folder.iterdir():
        if folder not in destination_folders.values():
            shutil.rmtree(folder)

    return result_lists


def unpacking(archives: Path):

    for item in archives.iterdir():
        
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
    
    create_folders(sortable_folder_copy)

    result_lists = sorter(sortable_folder_copy)
    
    print_result(result_lists)

    unpacking(destination_folders["archives"])


if __name__ == "__main__":
    main()
