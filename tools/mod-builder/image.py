from __future__ import annotations # to use type in python 3.7

from clut import get_clut, rgb2psx

import cv2
import logging
import pathlib
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

imgs = [] # global

class Image:
    """
    Class for texture image files

    Reads images
    Converts from palettised (P) to palettised with an alpha channel (PA)
    """
    def __init__(self, fname: str) -> None:
        path = pathlib.Path(fname)

        # validation checks
        self.valid = True # default
        if not path.exists():
            logger.error(f"Given path does not exist: {path}")
            self.valid = False
            return
        self.valid = self.check_naming_convention(path.stem)
        if not self.is_valid():
            return

        # Extract metadata
        fname_parts = path.stem.split("_")
        self.name = fname_parts[0]
        self.mode = int(fname_parts[7])
        self.x = int(fname_parts[1])
        self.y = int(fname_parts[2])
        self.address = (self.y * 2048) + (self.x * 2)
        self.w = int(fname_parts[5]) // (16 // self.mode)
        self.h = int(fname_parts[6])
        self.clut = get_clut(int(fname_parts[3]), int(fname_parts[4]), self.mode)
        self.img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        self.pil_img = PILImage.open(str(path))
        if self.pil_img.mode == "P":
            self.pil_img = self.pil_img.convert("PA")
        self.psx_img = bytearray()
        self.img_len = 0
        self.output_path = None

    @staticmethod
    def check_naming_convention(fname):
        """
        Any texture file should be of the form
        NAME_#_#_#_#_#_#_# (name with 7 numbers)
        """
        list_parts = fname.split('_')
        if len(list_parts) != 8:
            logger.exception(f"wrong naming convention for the texture for image: {fname}")
            return False

        return True

    def img2psx(self) -> None:
        count = 0 #lol
        if self.pil_img.mode != "PA":
            for row in self.img:
                if self.mode == 4:
                    for i in range(0, len(row), 2):
                        px1 = self.clut.get_offset(row[i])
                        px2 = self.clut.get_offset(row[i + 1])
                        if px1 == -1 or px2 == -1:
                            return
                        px = (px2 << 4) | px1
                        self.psx_img.append(px)
                elif self.mode == 8:
                    for px in row:
                        px = self.clut.get_offset(px)
                        if px == -1:
                            return
                        self.psx_img.append(px)
                elif self.mode == 16:
                    for px in row:
                        px = rgb2psx(px[2], px[1], px[0], px[3])
                        self.psx_img.append(px & 0xFF)
                        self.psx_img.append((px >> 8) & 0xFF)
        else: # image is palettised with an alpha channel (PA)
            for row in self.img:
                if self.mode == 4:
                    for i in range(0, len(row), 2):
                        px1 = list(self.pil_img.getdata(0))[count]
                        px2 = list(self.pil_img.getdata(0))[count+1]
                        count = count + 2
                        if px1 == -1 or px2 == -1:
                            return
                        px = (px2 << 4) | px1
                        self.psx_img.append(px)
                elif self.mode == 8:
                    for px in row:
                        px = list(self.pil_img.getdata(0))[count]
                        count = count + 1
                        if px == -1:
                            return
                        self.psx_img.append(px)
                elif self.mode == 16:
                    for px in row:
                        px = rgb2psx(px[2], px[1], px[0], px[3])
                        self.psx_img.append(px & 0xFF)
                        self.psx_img.append((px >> 8) & 0xFF)

    def set_path(self, path: str) -> None:
        self.output_path = path

    def get_path(self) -> str:
        return self.output_path

    def is_valid(self) -> bool:
        return self.valid

    def show(self) -> None:
        cv2.imshow('image', self.img)
        cv2.waitKey(0)

    def as_c_struct(self) -> str:
        """
        Replacing with triple quotes is possible but
        too much work to remove extra spacings
        """
        string_header = f"// CLUT = {self.clut.name}"
        string_function = f"char {self.name}[] = {{"
        for px in self.psx_img:
            string_function += hex(px) + ","
        string_function += "};"

        list_out = [
            string_header,
            string_function,
            "",
            # function body
            f"RECT {self.name}_pos = {{", 
            f"    .x = {str(self.x)},",
            f"    .y = {str(self.y)},",
            f"    .w = {str(self.w)},",
            f"    .h = {str(self.h)}",
            "};",
            ""
        ]

        return "\n".join(list_out)

    def __str__(self) -> str:
        """TODO: Replace with triple quotes"""
        buffer = ""
        if (self.clut is not None) and (self.clut.is_valid()):
            buffer += "IMG: " + self.name + "\n"
            buffer += "Coords: (" + str(self.x) + ", " + str(self.y) + ")\n"
            buffer += "Width, height: (" + str(self.w) + ", " + str(self.h) +")\n"
            buffer += "Address: " + hex(self.address) + "\n"
            buffer += '['
            for px in self.psx_img:
                buffer += hex(px) + ','
            buffer += ']\n'
        else:
            buffer += "ERROR: The images are adding too many colors to a single Image.\n"
        return buffer


def get_image_list() -> list[Image]:
    return imgs

def clear_images() -> None:
    imgs.clear()

def dump_images(path: str) -> None:
    print("\n[Image-py] Dumping images...")
    for img in imgs:
        if img.clut.is_valid():
            img_path = path + img.name + ".bin"
            img.set_path(img_path)
            with open(img_path, "wb") as file:
                file.write(img.psx_img)
        else:
            print("[Image-py] WARNING: Image " + img.name + " was ignored because it uses " + img.clut.name + ", which exceeds the number of maximum colors")

def create_images(directory: str) -> int:
    """
    Prefers a directory with .png files
    Affects the global images list
    # TODO: Replace .png with a regex of other file formats.
    """
    count_images = 0
    dir_path = pathlib.Path(directory)
    for path in list(dir_path.rglob('*.png')):
        count_images += 1
        logger.debug(path)
        img = Image(path)
        if img.is_valid():
            imgs.append(img) # global images list
            img.img2psx()
            if img.pil_img.mode == "PA":
                img.clut.add_indexed_colors(img.pil_img)
    return count_images