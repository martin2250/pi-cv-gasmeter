#!/usr/bin/python
import cv2
import os
import numpy as np

def findFileName(name):	#sample%s.xml
	i = 0
	while os.path.exists(name % i):
	    i += 1
	return name % i

def save(img, name):
	name = findFileName(name)
	cv2.imwrite(name, img)

def rateContourDigitArea(cnt):
	#width: 990 height:145
	rect = cv2.minAreaRect(cnt)
	w = max(rect[1])
	h = min(rect[1])

	return ((w - 990)**2 + (h - 145)**2)

def rateContourDigit(cnt):
	#width: 36 height: 80
	rect = cv2.minAreaRect(cnt)
	w = min(rect[1])
	h = max(rect[1])
	return ((w - 36)**2 + 1.5 * (h - 80)**2)

#extracts black (and red) box around digits and scales it to a fixed size
def getDigitArea(img):

	print '\t\t> thresholding'
	thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,141,0)

	print '\t\t> finding contours (digit box)'

	im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	contours = sorted(contours, key=rateContourDigitArea)[:1]

	rect = cv2.minAreaRect(contours[0])
	box = cv2.boxPoints(rect)
	box = np.int0(box)	#in (x, y)

	b1 = sorted(box, key=lambda pt: -pt[0] - pt[1])[0]	#lower right (lower == higher y)
	b2 = sorted(box, key=lambda pt: pt[0] - pt[1])[0]	#lower left
	b3 = sorted(box, key=lambda pt: pt[0] + pt[1])[0]	#upper left

	sizeX = 900
	sizeY = 150

	pts1 = np.float32([b1, b2, b3])
	pts2 = np.float32([[sizeX, sizeY], [0,sizeY], [0,0]])
	M = cv2.getAffineTransform(pts1,pts2)

	print '\t\t> transforming image'
	dst = cv2.warpAffine(img,M,(sizeX, sizeY))

	return dst[5:-5,5:750]

def kernel(size):
	kernel = np.ones((size,size),np.uint8)
	return kernel

def extractDigit(img, cnt):
	x,y,w,h = cv2.boundingRect(cnt)
	roi = img[y:y+h,x:x+w]
	return roi

def prepareDigits(img):
	img = img[::-1, ::-1]	#flip horizontally and vertically
	img = img[20:-20]

	img = np.uint8(img[:,:,1])	#best channel (least difference to red area)

	print '\t> extracting digit area'

	img = getDigitArea(img)		#isolate interesting area

	digitSize = (55, 104)
	digitPos = [(36, 17), (140, 17), (244, 16), (349, 16), (452, 16), (557, 18), (661, 16)]

	digits = []

	print '\t> isolating digits'

	for i in range(0, len(digitPos)):
		x = digitPos[i][0]
		y = digitPos[i][1]
		w = digitSize[0]
		h = digitSize[1]

		digit = img[y:y+h,x:x+w]

		t = np.mean(digit) + 20
		ret,digit = cv2.threshold(digit,t,255,cv2.THRESH_BINARY)

		im2, contours, hierarchy = cv2.findContours(digit.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = sorted(contours, key=rateContourDigit)
		digit = extractDigit(digit, contours[0])

		digits.append(digit)

	return digits
