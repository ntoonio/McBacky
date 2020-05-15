import datetime
import hashlib
import glob
import os
import time
import shutil
import re

from McBacky.common import isVersionPath, listFiles, hashFile

class Save():
	def __init__(self, savePath, backupPath):
		self.path = savePath.rstrip("/")
		self.backupPath = backupPath.rstrip("/")

	def listVersions(self):
		files = glob.glob(self.backupPath + "/*")

		for f in files:
			if os.path.isdir(f) and isVersionPath(f):
				yield f.replace(self.backupPath + "/", "")

	def hashFiles(self):
		for f in listFiles(self.path + "/"):
			h = hashFile(self.path + "/" + f)
			yield (h, f)

	def readManifest(self):
		versions = [x for x in self.listVersions()]
		versions.sort(reverse=True)

		if len(versions) == 0:
			return []

		manifestFile = self.backupPath + "/" + versions[0] + "/full_manifest.txt"

		with open(manifestFile) as f:
			for line in f:
				yield line.strip().split(";")

	def _writeManifest(self, dictManifest, dictNewManifest, time):
		manifestFile = self.backupPath + "/" + time + "/full_manifest.txt"
		versionManifestFile = self.backupPath + "/" + time + "/manifest.txt"

		# Overwrite dictManifest with dictNewManifest
		for d in dictNewManifest:
			dictManifest[d] = dictNewManifest[d]

		with open(manifestFile, "w") as f:
			for d in dictManifest:
				f.write(dictManifest[d] + ";" + d + "\n")

		with open(versionManifestFile, "w") as f:
			for d in dictNewManifest:
				f.write(dictNewManifest[d] + ";" + d + "\n")

	def _backupFile(self, f, time):
		"Add the file `f` (which is a path relative to the save root) to the backup of the time `time`"

		src = self.path + "/" + f # The file to copy
		destPath = self.backupPath + "/" + time + "/" + f # The location of the new file
		destDir = self.backupPath + "/" + time + "/" + os.path.dirname(f) # The directory to put the above mentioned file in

		if not os.path.exists(destDir):
			os.makedirs(destDir)

		shutil.copy(src, destPath)

	def createBackup(self, dryRun=False):
		now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
		backupDir = self.backupPath + "/" + now + "/"

		manifest = {}

		for m in self.readManifest():
			manifest[m[1]] = m[0]

		newManifest = {}

		for hf in self.hashFiles():
			if hf[1] not in manifest or hf[0] != manifest[hf[1]]:
				newManifest[hf[1]] = hf[0]

		if len(newManifest) != 0 and not dryRun:
			if not os.path.exists(backupDir):
				os.makedirs(backupDir)

			for m in newManifest:
				self._backupFile(m, now)
			self._writeManifest(manifest, newManifest, now)

		return (newManifest, now)
