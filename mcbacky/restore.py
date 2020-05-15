import datetime
import os
import glob
import shutil
import re

from McBacky.common import isVersionPath, readManifest

class Backup:
	def __init__(self, backupPath):
		self.path = backupPath.rstrip("/")

	def listVersions(self):
		files = glob.glob(self.path + "/*")

		for f in files:
			if os.path.isdir(f) and isVersionPath(f):
				yield f.replace(self.path + "/", "")

	def restore(self, restoreDir, fromVersion = None):
		now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
		restoreDir = self.path + "/restored_" + now

		if not os.path.exists(restoreDir):
			os.makedirs(restoreDir)

		versions = [x for x in self.listVersions()]
		versions.sort(reverse=True)

		if fromVersion == None:
			if len(versions) == 0:
				raise Exception("There are no backup versions in '{}'".format(self.path))

			fromVersion = versions[0]

		if not os.path.exists(self.path + "/" + fromVersion):
			raise Exception("Backup version '{}' doesn't exist".format(fromVersion))

		files = []

		for m in readManifest(self.path + "/" + fromVersion + "/full_manifest.txt"):
			files.append(m[1])

		for v in versions:
			if fromVersion != None and v > fromVersion:
				continue

			if len(files) == 0:
				break

			for m in readManifest(self.path + "/" + v + "/manifest.txt"):
				fileName = m[1]

				if fileName in files:
					files.remove(fileName)

					src = self.path + "/" + v + "/" + fileName
					dest = restoreDir + "/" + fileName
					shutil.copy(src, dest)
