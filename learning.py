#!/usr/bin/python
import cv2
import numpy as np
from vision import *
import os
import code

def digitToData(digit, width, height):
	digit = cv2.copyMakeBorder(digit,1,1,1,1,cv2.BORDER_CONSTANT,value=0)

	digitFilled = np.zeros(digit.shape)

	im2, contours, hierarchy = cv2.findContours(digit.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=rateContourDigit)[0]
	cv2.drawContours(digitFilled, contours, -1, 255, -1)

	digitsmall = cv2.resize(digit,(width,height))
	digitFsmall = cv2.resize(digitFilled,(width,height))


	digitsmall = digitsmall.reshape((1, width * height))
	digitFsmall = digitFsmall.reshape((1, width * height))

	data = np.append(digitsmall,digitFsmall,1)

	return np.float32(data)

def loadModel(width, height):
	samples =  np.empty((0, width * height * 2))
	responses = np.empty((0, 1))

	print '\t> iterating over training data'

	for i in range(0, 10):
		basepath = 'data/' + str(i) + '/'

		if not os.path.exists(basepath):
			print basepath, 'does not exist'
			exit()

		for imgpath in os.listdir(basepath):
			digit = cv2.imread(basepath + imgpath)
			digit = digit[:,:,0]

			data = digitToData(digit, width, height)

			out = np.zeros(10)
			out[i] = 1

			samples = np.append(samples,data,0)
			responses = np.append(responses,np.array([[i]], np.float32),0)

	samples = np.array(samples, np.float32)
	responses = np.array(responses,np.float32)
	responses = responses.reshape((responses.size,1))

	print '\t> creating and training model'
	print '\t> loaded', samples.shape[0], 'samples'

	model = cv2.ml.KNearest_create()
	model.train(samples, cv2.ml.ROW_SAMPLE,responses)
	return model
