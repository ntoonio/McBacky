import glob
import os

from mcbacky.common import WorldFile
from mcbacky.backup import Backup, BackupHistory

class World():
	def __init__(self, worldPath, backupPath, isBukkit = False):
		self.path = worldPath.rstrip("/")
		self.name = os.path.basename(worldPath)
		self.backups = BackupHistory(backupPath.rstrip("/"))

		self.isBukkit = isBukkit

	def getManifestFiles(self):
		backupVersions = self.backups.listBackups(reverse=True)

		if len(backupVersions) == 0:
			return False

		return backupVersions[0].getManifest()

	def getFiles(self):
		files = [WorldFile(x, x.replace(self.path + "/", "")) for x in glob.glob(self.path + "/**", recursive=True) if os.path.isfile(x)]

		if self.isBukkit:
			netherPath = os.path.dirname(self.path) + "/" + self.name + "_nether/DIM-1/"
			endPath = os.path.dirname(self.path) + "/" + self.name + "_the_end/DIM1/"

			netherFiles = glob.glob(netherPath + "/**", recursive=True)
			endFiles = glob.glob(endPath + "/**", recursive=True)

			files += [WorldFile(x, x.replace(netherPath, "DIM-1/")) for x in netherFiles if os.path.isfile(x)]
			files += [WorldFile(x, x.replace(endPath, "DIM1/")) for x in endFiles if os.path.isfile(x)]

		return files

	def generateManifest(self):
		manifest = {}

		latestManifest = self.getManifestFiles()
		if latestManifest != False:
			for f in latestManifest:
				manifest[f.shortPath] = f

		changedManifest = {}

		for f in self.getFiles():
			fileHash = f.fileHash()
			if f.shortPath not in manifest or fileHash != manifest[f.shortPath].fileHash(): # If the file is not in the manifest (ie it's new) or the hash of the has doesn't match that in the manifest (ie it has been changed)
				changedManifest[f.shortPath] = f

		return changedManifest, manifest

	def makeBackup(self):
		changedFiles, manifest = self.generateManifest()

		if len(changedFiles) == 0:
			return False

		backup = self.backups.createNewBackup()

		for cf in changedFiles:
			backup.addFile(changedFiles[cf])

		backup.writeManifest(changedFiles, manifest)

		return backup
