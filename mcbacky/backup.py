import os
import shutil
import glob
import datetime
import logging

from mcbacky.common import BackupFile, createNonCollidingPath

class Backup():
	def __init__(self, backupPath, locked = None):
		"`backupPath` is the the path of the backup directory. `locked` is used to block changes to already saved backups. If `None` (default) it looks for manifest.txt in the directory and assumes it should be locked if it exists"
		self.backupsDir = os.path.dirname(backupPath.rstrip("/"))
		self.name = os.path.basename(backupPath)

		self.path = backupPath.rstrip("/")
		self.manifestPath = self.path + "/manifest.txt"

		self.locked = locked if locked != None else os.path.exists(self.manifestPath)

	@staticmethod
	def isBackup(path):
		return os.path.exists(path.rstrip("/") + "/manifest.txt")

	def getManifest(self):
		"Returns list of `BackupFile`"

		logging.debug("Getting manifest")

		with open(self.manifestPath) as of:
			manifestFiles = []

			for line in of:
				# Line parts order: hash, file, backup
				lineParts = line.strip().split(";")

				manifestFiles.append(
					BackupFile(
						os.path.join(self.backupsDir, lineParts[2], lineParts[1]),
						lineParts[1],
						lineParts[0],
						lineParts[2]))

		logging.debug("Got manifest")

		return manifestFiles

	def addFile(self, f):
		if self.locked:
			raise Exception("Can't add file to locked backup")

		dest = self.path + "/" + f.shortPath
		destDir = os.path.dirname(dest)

		if not os.path.exists(destDir):
			os.makedirs(destDir)

		shutil.copy(f.path, dest)

	def writeManifest(self, changedManifest, manifest):
		self.locked = True

		with open(self.manifestPath, "w") as of:
			for f in changedManifest:
				ff = changedManifest[f]
				of.write(ff.fileHash() + ";" + ff.shortPath + ";" + self.name + "\n")

			for f in manifest:
				if f in changedManifest: continue
				ff = manifest[f]

				of.write(ff.fileHash() + ";" + ff.shortPath + ";" + ff.backupName + "\n")

	def restore(self, restoreDir):
		name = "World_restoration_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
		restorePath = createNonCollidingPath(restoreDir.rstrip("/") + "/" + name)

		manifest = self.getManifest()

		for m in manifest:
			src = m.path
			dest = os.path.join(restorePath, m.shortPath)

			destDir = os.path.dirname(dest)
			if not os.path.exists(destDir):
				os.makedirs(destDir)

			shutil.copy(src, dest)

		return manifest, restorePath

class BackupHistory:
	def __init__(self, backupsDir):
		self.path = backupsDir.rstrip("/")

	def listBackups(self, reverse=False):
		files = glob.glob(self.path + "/*")
		files.sort(reverse=reverse)

		return [Backup(f, self) for f in files if os.path.isdir(f) and Backup.isBackup(f)]

	def createNewBackup(self):
		name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
		backupPath = createNonCollidingPath(self.path + "/" + name)

		os.makedirs(backupPath)

		return Backup(backupPath)
