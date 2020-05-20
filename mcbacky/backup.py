import os
import shutil
import glob
import datetime

class Backup():
	def __init__(self, backupPath, locked = None):
		"`backupPath` is the the path of the backup directory. `locked` is used to block changes to already saved backups. If `None` (default) it looks for manifest.txt in the directory and assumes it should be locked if it exists"
		self.backupsDir = os.path.dirname(backupPath)
		self.name = os.path.basename(backupPath)

		self.path = self.backupsDir + "/" + self.name
		self.manifestPath = self.path + "/manifest.txt"

		self.locked = locked if locked != None else os.path.exists(self.manifestPath)

	@staticmethod
	def isBackup(path):
		return os.path.exists(path.rstrip("/") + "/manifest.txt")

	def getManifest(self):
		with open(self.manifestPath) as of:
			manifest = []
			readingNewFiles = True

			for line in of:
				if line == "-\n":
					readingNewFiles = False
					continue

				lineParts = line.strip().split(";")
				# hash, file, backup
				manifest.append([lineParts, readingNewFiles])

		return manifest

	def addFile(self, f, src):
		if self.locked:
			raise Exception("Can't add file to locked backup")

		dest = self.path + "/" + f
		destDir = os.path.dirname(dest)

		if not os.path.exists(destDir):
			os.makedirs(destDir)

		shutil.copy(src, dest)

	def writeManifest(self, changedManifest, manifest):
		self.locked = True

		with open(self.manifestPath, "w") as of:
			for f in changedManifest:
				of.write(changedManifest[f] + ";" + f + ";" + self.name + "\n")

			of.write("-\n")

			for f in manifest:
				if f in changedManifest: continue

				of.write(manifest[f][0] + ";" + f + ";" + manifest[f][1] + "\n")

class BackupHistory:
	def __init__(self, backupsDir):
		self.path = backupsDir.rstrip("/")

	def listBackups(self, reverse=False):
		files = glob.glob(self.path + "/*")
		files.sort(reverse=reverse)

		return [Backup(f) for f in files if os.path.isdir(f) and Backup.isBackup(f)]

	def createNewBackup(self):
		name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
		backupPath = self.path + "/" + name

		os.makedirs(backupPath)

		return Backup(backupPath)
