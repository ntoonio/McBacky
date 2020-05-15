import datetime
import hashlib
import glob
import os
import time
import shutil
import re

def isVersionPath(path):
	name = os.path.basename(path)
	return re.match("^\\d{4}(_\\d{2}){4}$", name) != None

def hashFile(fileName, chunkSize=32768):
	hasher = hashlib.md5()
	with open(fileName, "rb") as f:
		buf = f.read(chunkSize)
		while len(buf) > 0:
			hasher.update(buf)
			buf = f.read(chunkSize)
	return hasher.hexdigest()

def listFiles(directory):
	files = glob.glob(directory + "**/*", recursive=True)

	for f in files:
		if not os.path.isdir(f):
			yield f.replace(directory, "")

def readManifest(path):
	with open(path) as f:
		for line in f:
			yield line.strip().split(";")
