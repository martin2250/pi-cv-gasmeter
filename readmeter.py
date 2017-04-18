#!/usr/bin/python

#Martin Pittermann 04.2017

print '> loading modules'

import cv2
import numpy as np
import os
from vision import *
from learning import *
import subprocess
import code
import logging
import logging.handlers
import time

log = logging.getLogger('MyLogger')
log.setLevel(logging.DEBUG)
try:
	handler = logging.handlers.SysLogHandler(address = ('192.168.2.114',514), facility=19)
	log.addHandler(handler)
except:
	pass

logprefix = 'raspberry-pi-141 readmeter '

log.debug(logprefix + 'started reading')

datawidth = 10
dataheight = 10


print '> loading knearest model'
model = loadModel(datawidth, dataheight)


def readGasMeter():
	print '> open camera'
	cap = cv2.VideoCapture(0)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


	print '\t> pre-capture'
	for i in range(0, 10):
		cap.read()


	print '\t> reading image'
	ret, img = cap.read()

	#cv2.imwrite('latest.png', img)

	print '> extracting digits'
	digits = prepareDigits(img)


	print '> iterating over digits'

	result = 0.
	maxerror = 0

	for digit in digits:
		data = digitToData(digit, datawidth, dataheight)

		num, results, neigh_resp, dists = model.findNearest(data, k = 1)
		digiterror = dists[0][0] / 1e4

		result = result * 10 + num
		maxerror = max(maxerror, digiterror)

		print '\t> digit', int(num), 'error:', digiterror

	result = result / 100

	return result, maxerror

results = []

for i in range(0, 6):
	result, error = readGasMeter()

	results.append((result, error))

	if error < 30:
		break

	print 'error greater than 30 (%0.2f), reading again in 45 sek'%error

	time.sleep(45)


results = sorted(results, key=lambda r: r[1])

result, error = results[0]

print ''
print '> Zaehlerstand:', result, 'm^3'
print '> Fehler:', error

if error > 40:
	print 'min error too large (%0.2f), discarding data'%error
	log.error(logprefix + 'min error too large (%0.2f), discarding data'%error)
	exit()

print '> writing to database'

import pymysql

connection = pymysql.connect(host='',
                             user='',
							 password='',
                             db='')
try:
	with connection.cursor() as cursor:
		query = "INSERT INTO `Gas` (`Zaehlerstand`) VALUES (%s)"
		cursor.execute(query, (result))

	connection.commit()
finally:
	connection.close()

#os.system('shutdown -h now')
