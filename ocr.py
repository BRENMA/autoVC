from paddleocr import PaddleOCR
from os import listdir
from os.path import isfile, join

def ocrDeck():
    path = './SCREEN_SHOTS'
    filesRaw = [f for f in listdir(path) if isfile(join(path, f))]

    files = []
    for file in filesRaw:
        files.append(int(file.replace('.png', '')))

    total_files = max(files)
    print(total_files)

    deck_text = ""

    ocr = PaddleOCR(use_angle_cls=False, lang='en', show_log=False)

    i = 1
    while i <= total_files:
        img_path = f'./SCREEN_SHOTS/{i}.png'
        result = ocr.ocr(img_path, cls=False)
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                deck_text = deck_text + " " + line[1][0]

        i+=1

        print(f'current slide: {i} \n')

    return deck_text


