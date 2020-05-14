#!/usr/bin/python

import pyautogui, time
import sys
from PIL import Image
import math
import random

# todo: make keyboard interupt work (maybe right click to stop), add gui, add bounds for drawing. figure out color. add brush size. do one color at a time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPEED = 0.05


# remove transparent pixels by pasting original image over white background
def remove_transparent(file):
    image = Image.open(file)
    no_transparent = Image.new("RGB", image.size, "WHITE")
    no_transparent.paste(image, (0,0), image.convert('RGBA'))
    return no_transparent


def dither_image(file):
    return remove_transparent(file).convert('P', dither=Image.FLOYDSTEINBERG).convert('RGB')


def nearest_color_pic(file, color_map, dither=True):
    if dither:
        image = dither_image(file)
    else:
        image = remove_transparent(file).convert('RGB')
    width, height = image.size
    pixels = image.load()
    cache = {}

    for x in range(width):
        for y in range(height):
            color = pixels[x, y]
            if color in cache:
                pixels[x, y] = cache[color]
            else:
                near = nearest_color(color_map, color)
                pixels[x, y] = near
                cache[color] = near

    image.save('nearest_color.png')
    return image


def draw_line(len):  # modify length to make it darker (add more) or light (subtract)
    if len == 0:
        pyautogui.click()
    else:
        pyautogui.dragRel(len, 0, SPEED)


# random pauses to try to guarantee color gets clicked. sometimes it's too fast for the input buffer to keep up
def click_color(color_map, color, initial_position):
    if color in color_map:
        time.sleep(.01)
        pyautogui.moveTo(color_map[color][0], color_map[color][1], SPEED)
        time.sleep(.01)
        pyautogui.click()
        time.sleep(.01)
        pyautogui.click()
        time.sleep(.01)
        print('clicking color={}'.format(color))
        pyautogui.moveTo(initial_position[0], initial_position[1], SPEED)


# super slow
def draw_color(image, color_map):
    # initial values
    startX, startY = pyautogui.position()
    kill_height = pyautogui.size().height - 100  # prevent program from clicking menu bar
    drawStart = 0
    previous_color = WHITE
    width, height = image.size
    pixels = image.load()

    print('drawing image starting at x={}, y={}'.format(startX, startY))
    for y in range(height):
        if startY + y > kill_height:
            return
        drawStart = 0
        previous_color = WHITE

        for x in range(width):
            current_color = pixels[x, y]
            if current_color != previous_color: # color changed. finish current line
                if previous_color == WHITE and x != 0:  # skip over white pixels
                    pyautogui.moveTo(startX + x, startY + y, SPEED)
                else:  # draw previous color line up until this point
                    click_color(color_map, previous_color, (startX + drawStart, startY + y))
                    draw_line(x - drawStart - 1)
                    pyautogui.moveTo(startX + x, startY + y, SPEED)
                drawStart = x
                previous_color = current_color
        if previous_color != WHITE:  # finish drawing lines
            click_color(color_map, previous_color, (startX + drawStart, startY + y))
            draw_line(width - drawStart - 1)
    print('finished drawing')


# randomly assign keys to values
def shuffle_dict(d):
    shuffled = {}
    v = list(d.values())
    random.shuffle(v)
    return dict(zip(d.keys(), v))


def draw_one_color_each_pass(image, color_map, random=False):
    # initial values
    startX, startY = pyautogui.position()
    kill_height = pyautogui.size().height - 100  # prevent program from clicking menu bar
    drawStart = 0
    drawing = False
    width, height = image.size
    pixels = image.load()

    if random:
        color_map = shuffle_dict(color_map)

    print('drawing image starting at x={}, y={}'.format(startX, startY))
    for color in color_map:
        if color != WHITE:
            click_color(color_map, color, pyautogui.position())
            for y in range(height):
                if startY + y < kill_height:
                    drawStart = 0
                    drawing = False

                    for x in range(width):
                        current_color = pixels[x, y]
                        if current_color != color: # color changed. finish current line
                            if drawing:
                                drawing = False
                                pyautogui.moveTo(startX + drawStart, startY + y, SPEED)
                                draw_line(x - drawStart - 1)
                                pyautogui.moveTo(startX + x, startY + y, SPEED)
                        else:
                            if not drawing:
                                drawing = True
                                drawStart = x
                                
                    if drawing:  # finish drawing lines
                        pyautogui.moveTo(startX + drawStart, startY + y, SPEED)
                        draw_line(width - drawStart - 1)
    print('finished drawing')


def draw_color_picture(image, color_map, random=False):
    print('waiting 2 seconds')
    time.sleep(2)  # two seconds to get ready
    # draw_color(image, color_map)
    draw_one_color_each_pass(image, color_map, random)


# color closeness approximation from https://www.compuphase.com/cmetric.htm
def distance(c1, c2):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    r_mean = int((r1 + r2) / 2)
    r = r1 - r2
    g = g1 - g2
    b = b1 - b2
    return math.sqrt((((512 + r_mean) * r * r) >> 8) + 4 * g * g + (((767 - r_mean) * b * b) >> 8))


def nearest_color(color_map, color):
    return min(color_map, key=lambda c: distance(color, c))


def create_color_palette(file):
    color_map = {}
    start_offset = 10
    offset = 11
    location = pyautogui.locateOnScreen(file)
    if location is None:
        raise RuntimeError('Cannot find palette for file={}'.format(file))
    for y in range(location.top + start_offset, location.top + location.height, offset * 2):
        for x in range (location.left + start_offset, location.left + location.width, offset * 2):
            color_map[pyautogui.pixel(x, y)] = (x,y)
    return color_map


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: this_script.py <input file>')
    input_filename = sys.argv[1]
    pyautogui.PAUSE = 0.002
    pyautogui.FAILSAFE = True # upper left corner to kill program, but good luck getting there
    # log off or ctrl+alt+del to kill script

    # image = dither(input_filename)
    # draw_picture(image)

    dither = True
    random_colors = False
    color_map = create_color_palette('colors.png')
    image = nearest_color_pic(input_filename, color_map, dither)
    draw_color_picture(image, color_map, random_colors)


if __name__ == '__main__':
    main()
