#!/usr/bin/env python3
from PIL import Image, ImageEnhance
import warnings


class ImageColorMap(object):
    def __init__(
            self,
            url_image: str,
            height: int = 20,
            width: int = 40,
            contrast: float = 1.0,
            brightness: float = 1.0,
            show_background_color: bool = False,
            hide_foreground_character: bool = False,
            ascii_map: list = None):

        self.__url_image = url_image
        self.__height = height
        self.__width = width
        self.__contrast = contrast
        self.__brightness = brightness
        self.__show_background_color = show_background_color
        self.__hide_foreground_character = hide_foreground_character
        self.__ascii_lines = []
        self.__ascii_map = ascii_map if ascii_map else [
            ' ', '´', '.', ':', ';', 'i', '/', 'l', 'j', 'h',
            'N', 'S', 'k', 'W', 'M', 'G', '0', '@', '#', '#']

    @property
    def ascii_lines(self) -> list:
        if not self.__ascii_lines:
            self.__set_ascii_lines()
        return self.__ascii_lines

    def __set_ascii_lines(self):
        """
        print(im.format, im.size, im.mode)
        PPM (512, 512) RGB
        """
        # Image
        image = Image.open(self.__url_image, 'r')
        if image.mode != 'RGB':
            warnings.filterwarnings('ignore')  # Fix RGBA warning
            image = image.convert('RGB')

        # Resize
        h, w = image.size
        if h != self.__height or w != self.__width:
            image = image.resize(
                (self.__width, self.__height),
                Image.Resampling.BICUBIC)  # type: ignore

        # Adjust color
        if self.__contrast != 1.0:
            contrast = ImageEnhance.Contrast(image)
            image = contrast.enhance(self.__contrast)
        if self.__brightness != 1.0:
            brightness = ImageEnhance.Brightness(image)
            image = brightness.enhance(self.__brightness)

        # Map
        ascii_line = ''
        loop_count = 0
        line_count = 0
        for pixel in list(image.getdata()):
            if len(pixel) == 3:
                r, g, b = pixel
            else:
                r, g, b, _a = pixel

            # Foreground:
            #     set brightness to find ascii_map char index
            pixel_brightness = (  # brightness: github.com/EbonJaeger/asciifyer
                    (0.2126 * r) + (0.7152 * g) + (0.0722 * b))

            ascii_map_char_index = int(
                    (pixel_brightness / 255.0) * (len(self.__ascii_map)))

            foreground_character = ' '
            if not self.__hide_foreground_character:
                foreground_character = self.__ascii_map[ascii_map_char_index]

            # Background:
            #     \x1b[48... for background or \x1b[38... for hidden background
            bg_color = 48 if self.__show_background_color else 38
            ascii_line += '{}{}'.format(
                f'\x1b[{bg_color};2;{r};{g};{b}m',
                foreground_character)

            # Loop config
            if loop_count + 1 == self.__width:
                # Update line
                self.__ascii_lines.append(ascii_line + '\x1B[0m')
                line_count += 1

                # Reset
                ascii_line = ''
                loop_count = 0
            else:
                loop_count += 1

    @staticmethod
    def rgb_to_ansi(r: int, g: int, b: int, background: bool) -> str:
        return f"\x1b[{48 if background else 38};2;{r};{g};{b}m"


if __name__ == '__main__':
    pass