from aiopath import AsyncPath
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
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

destination_folders: Dict[str, AsyncPath] = {}

async def create_folders(parent: AsyncPath) -> None:

    for name in SUFFIXES.keys():

        new_folder: AsyncPath = parent / name
        await new_folder.mkdir()
        destination_folders[name] = new_folder


def normalize(name: str) -> str:

    translated_name = name.translate(TRANS)

    formatted_name = re.sub("\W", "_", translated_name)

    return formatted_name


def error_handler(func):
    def wrapper(*args):
        try:
            return func(*args)
        except (TooManyWordsError, UnchoosedDirectoryError) as error:
            print(error)
            sys.exit()
    return wrapper


async def move_file(file: AsyncPath) -> None:

    for folder in SUFFIXES:

        if file.suffix in SUFFIXES[folder]:
            new_name = f"{destination_folders[folder] / normalize(file.stem)}{file.suffix}"
            return await file.rename(new_name)

    new_name = f"{destination_folders['unknown'] / normalize(file.stem)}{file.suffix}"
    return await file.rename(new_name)


async def unpacking(archives: AsyncPath) -> None:

    async for item in archives.iterdir():
        
        shutil.unpack_archive(item, item.parent / item.stem)
        os.remove(item)


@error_handler
def get_sortable_folder() -> AsyncPath:

    if len(sys.argv) > 2:
        raise TooManyWordsError
    elif len(sys.argv) < 2:
        raise UnchoosedDirectoryError

    sortable_folder = AsyncPath(sys.argv[1])

    return sortable_folder


async def create_folder_copy(folder: AsyncPath) -> AsyncPath:
    
    parent: AsyncPath = folder.parent
    dst: AsyncPath = parent / (folder.stem + "_copy")

    if await dst.exists():
        shutil.rmtree(dst)
    
    copy = AsyncPath(shutil.copytree(folder, dst))
    
    return copy
    

async def main():

    sortable_folder = get_sortable_folder()

    sortable_folder_copy = await create_folder_copy(sortable_folder)
    
    await create_folders(sortable_folder_copy)

    files = [item async for item in sortable_folder_copy.rglob("*") if await item.is_file()]

    for file in files:
        await move_file(file)

    async for folder in sortable_folder_copy.iterdir():
        if folder not in destination_folders.values():
            shutil.rmtree(folder)

    await unpacking(destination_folders["archives"])


if __name__ == "__main__":
    asyncio.run(main())
