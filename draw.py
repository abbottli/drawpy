#!/usr/bin/python

import os
import sys

import pyautogui
import time
from PIL import Image

# todo: add bounds for drawing. refactor all of this
SPEED = 0.05
RESOURCE_FOLDER = 'resources'


# scuffed enum
class ImageType:
    BLACK_WHITE = 0
    DITHER = 1
    HALFTONE = 2


def resource_folder(file):
    return os.path.join(RESOURCE_FOLDER, file)


def convert_image(image, convert_type=ImageType.DITHER):
    if ImageType.DITHER == convert_type:
        return dither(image)
    elif ImageType.BLACK_WHITE == convert_type:
        return black_white(image)
    elif ImageType.HALFTONE == convert_type:
        return halftone(image)


def black_white(image):
    thresh = 128
    r = image.convert('L').point(lambda x: 255 if x > thresh else 0, mode='1')
    r.save(resource_folder('bw.png'))
    return r


def dither(image):
    image = image.convert('1')
    image.save(resource_folder('dither.png'))
    return image


def halftone(image):
    image = image.convert('L')
    width, height = image.size
    pixels = image.load()

    for x in range(0, width, 2):
        for y in range(0, height, 2):
            here, right, down, diag = (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)

            if x + 1 >= width:
                right = (0, 0)
                diag = (0, 0)
            if y + 1 >= height:
                down = (0, 0)
                diag = (0, 0)

            saturation = (pixels[here] + pixels[right] + pixels[down] + pixels[diag]) / 4

            if saturation > 223:  # all white
                pixels[here] = 255
                pixels[right] = 255
                pixels[down] = 255
                pixels[diag] = 255
            elif saturation > 159:
                pixels[here] = 255
                pixels[right] = 255
                pixels[down] = 0
                pixels[diag] = 255
            elif saturation > 95:
                pixels[here] = 255
                pixels[right] = 0
                pixels[down] = 0
                pixels[diag] = 255
            elif saturation > 23:
                pixels[here] = 0
                pixels[right] = 0
                pixels[down] = 0
                pixels[diag] = 255
            else:  # all black
                pixels[here] = 0
                pixels[right] = 0
                pixels[down] = 0
                pixels[diag] = 0

    image.save(resource_folder('halftone.png'))
    return image


# more info on resizing type https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters
def rescale_image(image, scale, scale_type=Image.BICUBIC):
    if scale != 1:
        scaled = tuple([int(x * scale) for x in image.size])
        resized = image.resize(scaled, scale_type)
        resized.save(resource_folder('resized.png'))
        return resized
    return image


def is_white(color):
    if type(color) is tuple:
        return color > (0, 0, 0)
    elif type(color) is int:
        return color > 0
    return True


def draw_line(length):  # modify length to make it darker (add more) or light (subtract)
    if length == 0:
        pyautogui.click()
    else:
        pyautogui.dragRel(length, 0, SPEED)


def draw(image):
    start_x, start_y = pyautogui.position()
    kill_height = pyautogui.size().height - 100  # prevent program from clicking menu bar
    array = image.load()  # assumes single value color probably need some type(x) is check
    width, height = image.size

    for y in range(height):
        if start_y + y > kill_height:
            return
        drawing = False
        draw_start = 0
        for x in range(width):
            if is_white(array[x, y]):  # if white
                if drawing:  # draw line up until this point
                    drawing = False
                    pyautogui.moveTo(start_x + draw_start, start_y + y, SPEED)
                    draw_line(x - draw_start - 1)
                    pyautogui.moveTo(start_x + x, start_y + y, SPEED)
            else:  # if black
                if not drawing:  # move cursors to beginning of line
                    drawing = True
                    draw_start = x
        if drawing:
            draw_line(width - draw_start - 1)


def draw_picture(image):
    time.sleep(2)  # two seconds to get ready
    draw(image)


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: this_script.py <input file>')
    input_filename = sys.argv[1]
    pyautogui.PAUSE = 0.002
    pyautogui.FAILSAFE = True  # upper left corner to kill program, but good luck getting there
    # log off or ctrl+alt+del to kill script

    if not os.path.exists(RESOURCE_FOLDER):
        os.mkdir(RESOURCE_FOLDER)

    scale = 1

    image = Image.open(input_filename)
    image = rescale_image(image, scale)
    image = convert_image(image, convert_type=ImageType.DITHER)
    draw_picture(image)


if __name__ == '__main__':
    main()
