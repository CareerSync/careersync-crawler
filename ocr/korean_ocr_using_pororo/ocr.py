from main import PororoOcr

ocr = PororoOcr()
image_path = '../data/ttt.jpeg'
text = ocr.run_ocr(image_path, debug=False)
print('Result :', text)