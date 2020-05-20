import os
import pyautogui
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageTk, Image
from enum import Enum
import draw as drawbw
import drawcolor


RESOURCE_FOLDER = 'resources'
palette = 'colors.png'
DRAW_OPTIONS = [
    'BW',
    'BW Halftone',
    'BW Dither',
    'Color',
    'Color Dither'
]
COLOR_DRAWTYPE_OPTIONS = [
    'One Color Each Pass',
    'All Colors At Once'
]
SCALE_OPTIONS = [
    'Nearest',
    'Box',
    'Bilinear',
    'Hamming',
    'Bicubic',
    'Lanczos'
]
BASE_WIDTH = 300
BASE_HEIGHT = 300
base_image = Image.new("RGB", (BASE_WIDTH, BASE_HEIGHT), "WHITE")
converted_image = base_image
window = tk.Tk()
draw_choice = tk.StringVar()
scale_choice = tk.StringVar()
color_map = {}

def draw():
    global color_map
    print('drawing')
    draw_type = draw_choice.get()
    if draw_type.startswith('BW'):
        drawbw.draw_picture(converted_image)
    elif draw_type.startswith('Color'):
        color_map = drawcolor.create_color_palette(palette)  # recalculate coors for colors in case it moved
        drawcolor.draw_color_picture(converted_image, color_map, random=False)
    print('done drawing')


def swap_image(panel, swap_image):
    tk_image = ImageTk.PhotoImage(swap_image)
    panel.configure(image = tk_image)
    panel.image = tk_image  # save so image isn't deleted by gc


def convert_image(converted_image_panel, scale_entry):
    global base_image
    global converted_image
    draw_type = draw_choice.get()
    scale_type = scale_choice.get()

    converted_image = drawbw.rescale_image(base_image, float(scale_entry.get()), SCALE_OPTIONS.index(scale_type))

    if 'BW' == draw_type:
        converted_image = drawbw.blackwhite(converted_image)
    elif 'BW Halftone' == draw_type:
        converted_image = drawbw.halftone(converted_image)
    elif 'BW Dither' == draw_type:
        converted_image = drawbw.dither(converted_image)
    elif 'Color' == draw_type:
        converted_image = drawcolor.nearest_color_pic(converted_image, color_map, dither=False)
    elif 'Color Dither' == draw_type:
        converted_image = drawcolor.nearest_color_pic(converted_image, color_map, dither=True)
    else:
        converted_image = converted_image
    width, height = converted_image.size
    a, b = base_image.size

    swap_image(converted_image_panel, converted_image)


def open_file(base_image_panel, converted_image_panel, scale_entry):
    filepath = askopenfilename(
        filetypes=[("All Files", "*.*")]
    )
    if not filepath:
        return
    global base_image
    scale_entry.delete(0, tk.END)
    scale_entry.insert(0, '1')  # reset scale

    base_image = drawcolor.remove_transparent(Image.open(filepath))
    swap_image(base_image_panel, base_image)

    convert_image(converted_image_panel, scale_entry)

    window.title(f"DrawPy - {os.path.basename(filepath)}")


def main():
    global color_map

    if not os.path.isfile(palette):
        raise RuntimeError('Unable to find provided color palette for file={}'.format(palette))
    if not os.path.exists(RESOURCE_FOLDER):
        os.mkdir(RESOURCE_FOLDER)

    color_map = drawcolor.create_color_palette(palette)  # palette needs to be on the screen. screen color changers might mess with this

    pyautogui.PAUSE = 0.002
    pyautogui.FAILSAFE = True
    window.title("DrawPy")

    # grid configs
    window.rowconfigure(0, weight=1)
    window.columnconfigure([1, 2], minsize=50, weight=1)

    # frames
    fr_buttons = tk.Frame(window)
    fr_base = tk.Frame(window)
    fr_converted = tk.Frame(window)

    # widgets
    base_label = tk.Label(fr_base, text='Original Image')
    converted_label = tk.Label(fr_converted, text='Converted Image')
    scale_label = tk.Label(fr_buttons, text='Scale')
    scale_entry = tk.Entry(fr_buttons, width=3)
    scale_entry.insert(0, '1')
    draw_choice.set(DRAW_OPTIONS[2])
    draw_dropdown = tk.OptionMenu(fr_buttons, draw_choice, *DRAW_OPTIONS, command=lambda x: convert_image(converted_image_panel, scale_entry))
    scale_choice.set(SCALE_OPTIONS[4])
    scale_dropdown = tk.OptionMenu(fr_buttons, scale_choice, *SCALE_OPTIONS, command=lambda x: convert_image(converted_image_panel, scale_entry))

    tk_image = ImageTk.PhotoImage(base_image)
    base_image_panel = tk.Label(fr_base, image=tk_image)
    converted_image_panel = tk.Label(fr_converted, image=tk_image)
    btn_open = tk.Button(fr_buttons, text="Open", command=lambda: open_file(base_image_panel, converted_image_panel, scale_entry))

    btn_draw = tk.Button(window, text='Draw', command=draw)

    # placements
    btn_open.pack()
    draw_dropdown.pack()
    scale_label.pack(side=tk.LEFT)
    scale_entry.pack(side=tk.LEFT)

    base_label.pack()
    base_image_panel.pack()

    converted_label.pack()
    converted_image_panel.pack()

    fr_buttons.grid(row=0, column=0, sticky="nw")
    fr_base.grid(row=0, column=1, sticky='nswe')
    fr_converted.grid(row=0, column=2, sticky='nswe')
    btn_draw.grid(row=1, column=0, sticky='sw')

    window.mainloop()


if __name__ == '__main__':
    main()
