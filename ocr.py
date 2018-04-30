from extract import extract
from api import insert_event
from PIL import Image
import cv2
import pytesseract
import re
import numpy as np
from matplotlib import pyplot as plt

def img_to_txt(filename=''):
	if filename == '': #default image
		img = cv2.imread('./static/ku.jpg')
	else:
		print('not using deafult bro')
		img = cv2.imread('.' + filename)
		print('.'+filename)

	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	#show histogram
	# plt.hist(img.ravel(), 256, [0, 256])
	# plt.show()

	retval, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

	# cv2.imshow('img',img)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	cv2.imwrite('./static/processed_image.jpg', img)
	text = pytesseract.image_to_string(img)

	data = extract(text)
	return data