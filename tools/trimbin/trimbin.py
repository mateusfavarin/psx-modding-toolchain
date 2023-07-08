"""
Called by nugget/common.mk
TODO: Move to the mod-bulider
"""
import logging
import os
import pathlib
import sys

# import _files

logger = logging.getLogger(__name__)

def trimbin(filename: str, target_path: str, offset_file: str) -> None:
    logger.debug("filename", filename)
    logger.debug("target_path", target_path)
    logger.debug("offset_file", offset_file)
    arr = bytearray()
    with open(filename, "rb") as file:
        arr = file.read()

    extension = pathlib.Path(filename).suffix.replace(".", "")
    with open(offset_file, "r") as file:
        for line in file:
            line = line.split()
            if line[0] == extension:
                arr = arr[int(line[1], 0):]
                break

    with open(filename, "wb") as file:
        file.write(arr)

    new_name = extension + ".bin"
    new_filename = pathlib.Path(target_path) / new_name
    if new_filename.exists():
        new_filename.unlink()
    os.rename(filename, new_filename)

def main() -> None:
    trimbin(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()