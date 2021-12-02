import argparse
import io
import json
import os
from enum import Enum
from pathlib import Path

import cv2
from google.cloud import vision
from tqdm import tqdm

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'manga-ocr-333814-4fa21e4a4d24.json'


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def draw_boxes(image_path, words_info, color):
    np_img = cv2.imread(image_path)
    for key in words_info.keys():
        cv2.rectangle(
            np_img, words_info[key]['bbox'][0], words_info[key]['bbox'][1],
            color=color, thickness=7, lineType=cv2.LINE_4
        )
        cv2.putText(np_img, key, words_info[key]['bbox'][0], cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), 5, cv2.LINE_AA)
    return np_img


def extract_words(document, feature):
    words_info = {}
    paragraph_id = 0
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                p_key = f'id_{str(paragraph_id)}'
                words_info[p_key] = {}
                content_text = ''
                for word in paragraph.words:
                    content_text += ''.join([symbol.text for symbol in word.symbols])
                words_info[p_key]['bbox'] = [
                    (paragraph.bounding_box.vertices[0].x, paragraph.bounding_box.vertices[0].y),
                    (paragraph.bounding_box.vertices[2].x, paragraph.bounding_box.vertices[2].y),
                ]
                words_info[p_key]['content'] = str(content_text)
            paragraph_id += 1
    return words_info


def main(input_dir, output_dir):
    output_dir = Path(output_dir)
    json_dir = output_dir / 'json'
    img_dir = output_dir / 'img'
    json_dir.mkdir(exist_ok=True, parents=True)
    img_dir.mkdir(exist_ok=True, parents=True)
    client = vision.ImageAnnotatorClient()
    for file_path in tqdm(list(Path(input_dir).glob("*[png|jpg|jpeg|PNG|JPG|JPEG]"))):
        with io.open(str(file_path), 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        response = client.document_text_detection(
                image=image,
                image_context={'language_hints': ['ja']}
        )
        document = response.full_text_annotation
        words_info = extract_words(document, FeatureType.WORD)
        with open(str(json_dir / f'{file_path.stem}.json'), 'w') as f:
            json.dump(words_info, f, indent=4, ensure_ascii=False)
        # with open(str(json_dir / f'{file_path.stem}.json'), 'r') as f:
        #     words_info = json.load(f)

        result_image = draw_boxes(str(file_path), words_info, (0, 0, 255))
        cv2.imwrite(str(img_dir / f'{file_path.stem}.png'), result_image)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", required=True)
    parser.add_argument("-o", "--output_dir", required=True)
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
