import os
import shutil
import glob
import datetime

from mcbacky.common import BackupFile, randomString, createNonCollidingName

class Backup():
	def __init__(self, backupPath, locked = None):
		"`backupPath` is the the path of the backup directory. `locked` is used to block changes to already saved backups. If `None` (default) it looks for manifest.txt in the directory and assumes it should be locked if it exists"
		self.backupsDir = os.path.dirname(backupPath)
		self.name = os.path.basename(backupPath)

		self.path = backupPath.rstrip("/")
		self.manifestPath = self.path + "/manifest.txt"

		self.locked = locked if locked != None else os.path.exists(self.manifestPath)

	@staticmethod
	def isBackup(path):
		return os.path.exists(path.rstrip("/") + "/manifest.txt")

	def getManifest(self):
		with open(self.manifestPath) as of:
			manifestFiles = []

			for line in of:
				# Line parts order: hash, file, backup
				lineParts = line.strip().split(";")

				manifestFiles.append(
					BackupFile(
						self.path + "/" + lineParts[1],
						lineParts[1],
						lineParts[0],
						lineParts[2]))

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

class BackupHistory:
	def __init__(self, backupsDir):
		self.path = backupsDir.rstrip("/")

	def listBackups(self, reverse=False):
		files = glob.glob(self.path + "/*")
		files.sort(reverse=reverse)

		return [Backup(f) for f in files if os.path.isdir(f) and Backup.isBackup(f)]

	def createNewBackup(self):
		originalName = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
		name = createNonCollidingName(originalName, self.path + "/")

		backupPath = self.path + "/" + name

		os.makedirs(backupPath)

		return Backup(backupPath)
