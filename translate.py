import argparse
import json
import os
import subprocess as sp
import tempfile
from pathlib import Path

import cv2
import deepl

from const import *
from private_const import DEEPL_AUTH_KEY
from util import draw_boxes


def format_target_content(target_content):
    format_content = ''
    num_words = 0
    for i, word in enumerate(target_content.split(' ')):
        num_words += len(word) + 1
        format_content += word
        if num_words > NUM_WORDS_IN_LINE:
            format_content += '\n'
            num_words = 0
        else:
            format_content += ' '
    return format_content


def main(input_dir, is_translate):
    input_dir = Path(input_dir)
    orig_img_dir = input_dir / ORIG_IMG_DIR
    orig_json_dir = input_dir / ORIG_JSON_DIR
    target_json_dir = input_dir / TARGET_JSON_DIR
    gimp_dir = input_dir / GIMP_DIR
    target_json_dir.mkdir(exist_ok=True)
    gimp_dir.mkdir(exist_ok=True)

    if is_translate:
        translator = deepl.Translator(DEEPL_AUTH_KEY) 
        for json_path in list(orig_json_dir.glob("*[json]")):
            print(f"translate {json_path}...")
            with open(str(json_path), 'r') as f:
                words_info = json.load(f)
            new_words_info = words_info.copy()

            for words_id in words_info.keys():
                result = translator.translate_text(
                    words_info[words_id]['content'], target_lang=TARGET_LANG
                )
                new_words_info[words_id]['content'] = format_target_content(str(result))
            
            with open(str(target_json_dir / json_path.name), 'w') as f:
                json.dump(new_words_info, f, indent=4, ensure_ascii=False)
        
    for json_path in list(target_json_dir.glob("*[json]")):
        print(f"create gimp from {json_path}...")
        with open(str(json_path), 'r') as f:
            new_words_info = json.load(f)

        # create no serif img.
        with tempfile.TemporaryDirectory() as tmp_dir:
            no_serif_img_path = os.path.join(tmp_dir, json_path.stem + '.png')
            img = draw_boxes(
                str(Path(orig_img_dir / (json_path.stem + '.png'))),
                new_words_info, (255, 255, 255), is_check=False
            )
            cv2.imwrite(no_serif_img_path, img)

            save_path = gimp_dir / (json_path.stem + '.xcf')
            os.system(
                'gimp -id --batch-interpreter python-fu-eval -b ' +
                '"import sys;sys.path=[\'.\']+sys.path;' +
                f'import create_gimp;create_gimp.main(\'{no_serif_img_path}\', \'{json_path}\', \'{save_path}\')" ' +
                '-b "pdb.gimp_quit(1)"'
            )
    print('finish!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", required=True)
    parser.add_argument("--is_translate", action='store_true')
    args = parser.parse_args()
    main(args.input_dir, args.is_translate)
    
