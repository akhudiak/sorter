from aiopath import AsyncPath
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import sys
from typing import Dict

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
    "images": [".jpeg", ".JPG", ".png", ".jpg", ".svg"],
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


def move_file(file: Path) -> None:

    for folder in SUFFIXES:

        if file.suffix in SUFFIXES[folder]:
            Path(shutil.move(file, destination_folders[folder]))

    Path(shutil.move(file, destination_folders["unknown"]))


def unpacking(archives: Path) -> None:

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

    files = [i for i in sortable_folder_copy.rglob("*") if i.is_file()]

    with ThreadPoolExecutor(max_workers=40) as executor:
        executor.map(move_file, files)

    for folder in sortable_folder_copy.iterdir():
        if folder not in destination_folders.values():
            shutil.rmtree(folder)

    unpacking(destination_folders["archives"])


if __name__ == "__main__":
    main()
