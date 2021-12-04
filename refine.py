import json
import os
import sys
import tempfile
from pathlib import Path
from const import *

import cv2
from kivy.app import App
from kivy.config import Config
from kivy.core.text import DEFAULT_FONT, LabelBase
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.resources import resource_add_path
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

from util import draw_boxes

resource_add_path('./fonts')
LabelBase.register(DEFAULT_FONT, 'mplus-2c-regular.ttf')
Config.set('graphics', 'width', '1470')
Config.set('graphics', 'height', '1080')


class LoadDialog(FloatLayout):
    source = StringProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    json_dir = StringProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    source = StringProperty(None)
    json_path = StringProperty()

    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.json_path = 'None'

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(
            title="Load file", content=content, size_hint=(0.9, 0.9)
        )
        self._popup.open()

    def load(self, path, filename):
        self.json_path = os.path.join(path, filename[0])
        self.img_path = str(Path(str(filename[0])).parents[1] / ORIG_IMG_DIR / str(Path(str(filename[0])).stem + '.png'))
        with open(self.json_path, 'r') as f:
            self.words_info = json.load(f)

        # create kivy display text
        display_text = ''
        for words_id in self.words_info.keys():
            words = f"{words_id}: {self.words_info[words_id]['content']}"
            display_text += words + '\n'
        self.text_input.text = display_text

        # create box drawn image for kivy GUI
        # save image to tmp dir for kivy GUI Image api interface
        with tempfile.TemporaryDirectory() as tmpdir:
            show_img = draw_boxes(self.img_path, self.words_info, (0, 0, 255))
            tmp_img_path = os.path.join(tmpdir, 'tmp.png')
            cv2.imwrite(tmp_img_path, show_img)
            self.source = tmp_img_path

        self.dismiss_popup()

    def save(self):
        # update json
        # self.text_input.text: "id_xxx:Texts Detected by OCR.\n..."
        new_words_content = {}
        for words in self.text_input.text.split('\n'):
            if words == '':
                continue
            new_words_content[words.split(':')[0]] = words[len(words.split(':')[0]) + 1:]
        new_words_info = {k: v for k, v in self.words_info.items() if k in new_words_content.keys()}
        for k in new_words_content.keys():
            new_words_info[k]['content'] = new_words_content[k]

        with open(self.json_path, 'w') as f:
            json.dump(new_words_info, f, indent=4, ensure_ascii=False)

        # create kivy box drawn image
        # save image to tmp dir for kivy GUI Image api interface
        with tempfile.TemporaryDirectory() as tmpdir:
            show_img = draw_boxes(self.img_path, new_words_info, (0, 0, 255))
            tmp_img_path = os.path.join(tmpdir, 'tmp.png')
            cv2.imwrite(tmp_img_path, show_img)
            self.source = tmp_img_path

        self.dismiss_popup()


class Refine(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == "__main__":
    # TODO: Currently, set default load dir via class arg. It might be better instance arg ?.
    LoadDialog.json_dir = sys.argv[1]
    Refine().run()
