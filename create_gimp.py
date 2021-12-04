# witten in Python 2 (for python-fu)
import pdb
import glob
import json
import os
import sys

import gimp
from gimpfu import *
from const import *


def main(input_img_path, json_path, save_path):
    with open(json_path, 'r') as f:
        words_info = json.load(f)

    image = pdb.gimp_file_load(input_img_path, 'base')
    for words_id in words_info.keys():
        content = words_info[words_id]['content']
        left_up = words_info[words_id]['bbox'][0]
        bottom_down = words_info[words_id]['bbox'][1]

        # add white background layer for each serif.
        text_layer = pdb.gimp_text_layer_new(image, content, TARGED_FONT_NAME, WORD_SIZE, 0)
        center_x = int((left_up[0] + bottom_down[0]) / 2)
        center_y = int((left_up[1] + bottom_down[1]) / 2)
        new_left_up_x = center_x - text_layer.width // 2
        new_left_up_y = center_y - text_layer.height // 2
        white_layer = pdb.gimp_layer_new(image, text_layer.width, text_layer.height, 0, words_id + "_white", 100, 0)
        white_layer.set_offsets(new_left_up_x, new_left_up_y)
        white_layer.fill(1)
        image.add_layer(white_layer)

        text_layer.set_offsets(new_left_up_x, new_left_up_y)
        image.add_layer(text_layer)

    pdb.gimp_xcf_save(0, image, text_layer, save_path, save_path)
