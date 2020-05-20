import datetime
import hashlib
import glob
import os
import time
import shutil
import re

from mcbacky.backup import Backup, BackupHistory

class World():
	def __init__(self, worldPath, backupPath, isBukkit = False):
		self.path = worldPath.rstrip("/")
		self.name = os.path.basename(worldPath)
		self.backups = BackupHistory(backupPath.rstrip("/"))

		self.isBukkit = isBukkit

	def getManifestFiles(self):
		backupVersions = self.backups.listBackups()

		if len(backupVersions) == 0:
			return False

		return backupVersions[0].getManifest()

	def getFiles(self):
		files = [x.replace(self.path + "/", "") for x in glob.glob(self.path + "/**", recursive=True) if os.path.isfile(x)]

		if self.isBukkit:
			netherPath = os.path.dirname(self.path) + "/" + self.name + "_nether/DIM-1/"
			endPath = os.path.dirname(self.path) + "/" + self.name + "_the_end/DIM1/"

			netherFiles = glob.glob(netherPath + "/**", recursive=True)
			endFiles = glob.glob(endPath + "/**", recursive=True)

			files += [x.replace(netherPath, "DIM-1/") for x in netherFiles if os.path.isfile(x)]
			files += [x.replace(endPath, "DIM1/") for x in endFiles if os.path.isfile(x)]

		return [f.replace(self.path + "/", "") for f in files]

	def getAbsPath(self, f):
		if self.isBukkit:
			if f.startswith("DIM-1"): return os.path.dirname(self.path) + "/" + self.name + "_nether/" + f
			elif f.startswith("DIM1"): return os.path.dirname(self.path) + "/" + self.name + "_the_end/" + f

		return self.path + "/" + f

	def generateManifest(self):
		manifest = {}

		latestManifest = self.getManifestFiles()
		if latestManifest != False:
			for m in latestManifest:
				manifest[m[0][1]] = [m[0][0], m[0][2]]

		changedManifest = {}

		for f in self.getFiles():
			fileHash = hashFile(self.getAbsPath(f))
			if f not in manifest or fileHash != manifest[f][0]: # If the file is not in the manifest (ie it's new) or the file of the has doesn't match that in the manifest (ie it has been changed)
				changedManifest[f] = fileHash

		return changedManifest, manifest

	def makeBackup(self):
		changedFiles, manifest = self.generateManifest()

		if len(changedFiles) == 0:
			return False

		backup = self.backups.createNewBackup()

		for cf in changedFiles:
			backup.addFile(cf, self.getAbsPath(cf))

		backup.writeManifest(changedFiles, manifest)

		return backup

def hashFile(fileName, chunkSize=32768):
	hasher = hashlib.md5()
	with open(fileName, "rb") as f:
		buf = f.read(chunkSize)
		while len(buf) > 0:
			hasher.update(buf)
			buf = f.read(chunkSize)
	return hasher.hexdigest()