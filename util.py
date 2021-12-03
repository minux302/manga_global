import cv2


def draw_boxes(image_path, words_info, color):
    np_img = cv2.imread(image_path)
    for key in words_info.keys():
        cv2.rectangle(
            np_img, words_info[key]['bbox'][0], words_info[key]['bbox'][1],
            color=color, thickness=7, lineType=cv2.LINE_4
        )
        cv2.putText(np_img, key, words_info[key]['bbox'][0], cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), 5, cv2.LINE_AA)
    return np_img
