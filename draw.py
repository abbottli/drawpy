#!/usr/bin/python

import pyautogui, time
import sys
from PIL import Image


# todo: fix halftone, make keyboard interupt work (maybe right click to stop), add gui, add bounds for drawing. figure out color


def get_speed(distance):
    return max(0, distance/10000)


def map_to_grey(x):
    if x > 128:
        if x > 196:
            return 255
        else:
            return 196
    if x > 64:
        return 64
    return 0


def greyscale():
    img = Image.open('bamgotcha.jpg').resize((500,500))
    r = img.convert('L').point(map_to_grey, mode='L')
    r.save('grey.png')
    return r


def blackwhite(file):
    img = Image.open(file)
    thresh = 128
    fn = lambda x : 255 if x > thresh else 0
    r = img.convert('L').point(fn, mode='1')
    r.save('bw.png')
    return r

def dither(file):
    img = Image.open(file).convert('1')
    img.save('dither.png')
    return img


def halftone(file):
    image = Image.open(file).convert('L')
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

    image.save('halftone.png')
    return image


def is_white(color):
    if type(color) is tuple:
        return color > (0, 0, 0)
    elif type(color) is int:
        return color > 0;
    return True;


def draw_line(len):  # modify length to make it darker (add more) or light (subtract)
    if len == 0:
        pyautogui.click()
    else:
        pyautogui.dragRel(len, 0, .01)


def draw(image):
    startX, startY = pyautogui.position()
    kill_height = pyautogui.size().height - 100  # prevent program from clicking menu bar
    drawing = False
    drawStart = 0
    pyautogui.click()
    array = image.load()  # assumes single value color probably need some type(x) is check
    width, height = image.size

    for y in range(height):
        if startY + y > kill_height:
            return
        pyautogui.moveTo(startX, startY + y)  # move to next line
        drawing = False
        drawStart = 0
        for x in range(width):
            if is_white(array[x, y]):  # if white
                if drawing:  # draw line up until this point
                    drawing = False
                    draw_line(x - drawStart - 1)
            else:  # if black
                if not drawing:  # move cursors to beginning of line
                    drawing = True
                    drawStart = x
                    pyautogui.moveTo(startX + x, startY + y)
        if drawing:
            draw_line(width - drawStart)


def draw_picture(image):
    time.sleep(2)  # two seconds to get ready
    draw(image)


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: this_script.py <input file>')
    input_filename = sys.argv[1]
    pyautogui.PAUSE = 0.001
    pyautogui.FAILSAFE = True # upper left corner to kill program, but good luck getting there

    image = dither(input_filename)
    # draw_picture(image)


if __name__ == '__main__':
    main()
