import glob
import os
import logging

from mcbacky.common import WorldFile
from mcbacky.backup import Backup, BackupHistory

class World():
	def __init__(self, worldPath, backupPath, isBukkit = False):
		self.path = worldPath.rstrip("/")
		self.name = os.path.basename(worldPath)
		self.backups = BackupHistory(backupPath.rstrip("/"))

		self.isBukkit = isBukkit

	def getManifestFiles(self):
		logging.debug("Getting manifest files")

		backupVersions = self.backups.listBackups(reverse=True)
		logging.debug("Got all backup versions")

		if len(backupVersions) == 0:
			logging.debug("There are no backup versions")
			return False

		logging.debug("Getting manifest from the latest backup version")

		return backupVersions[0].getManifest()

	def getFiles(self):
		logging.debug("Getting files")

		files = [WorldFile(x, x.replace(self.path + "/", "")) for x in glob.glob(self.path + "/**", recursive=True) if os.path.isfile(x)]

		logging.debug("Got all world files")

		if self.isBukkit:
			logging.debug("The world is using the bukkit world structure")

			netherPath = os.path.dirname(self.path) + "/" + self.name + "_nether/DIM-1/"
			endPath = os.path.dirname(self.path) + "/" + self.name + "_the_end/DIM1/"

			netherFiles = glob.glob(netherPath + "/**", recursive=True)
			endFiles = glob.glob(endPath + "/**", recursive=True)

			files += [WorldFile(x, x.replace(netherPath, "DIM-1/")) for x in netherFiles if os.path.isfile(x)]
			files += [WorldFile(x, x.replace(endPath, "DIM1/")) for x in endFiles if os.path.isfile(x)]

			logging.debug("Added nether and the end files")

		logging.debug("Got all files")

		return files

	def generateManifest(self):
		logging.debug("Generating manifest")
		manifest = {}

		latestManifest = self.getManifestFiles()
		if latestManifest != False:
			for f in latestManifest:
				manifest[f.shortPath] = f

		logging.debug("Added latest manifest files")

		changedManifest = {}

		logging.debug("Comparing files with hashes...")

		files = self.getFiles()
		i = 1
		for f in files:
			fileHash = f.fileHash()
			if f.shortPath not in manifest or fileHash != manifest[f.shortPath].fileHash(): # If the file is not in the manifest (ie it's new) or the hash of the has doesn't match that in the manifest (ie it has been changed)
				changedManifest[f.shortPath] = f
				logging.debug("File '{}' has changed (processed {}/{} files)".format(f.shortPath, i, len(files)))
			i += 1

		logging.debug("Added changed files to manifest")
		logging.debug("Generated manifest")

		return changedManifest, manifest

	def makeBackup(self):
		logging.debug("Making backup")

		changedFiles, manifest = self.generateManifest()

		if len(changedFiles) == 0:
			logging.debug("There are no changed files... returning")
			return False

		backup = self.backups.createNewBackup()

		logging.debug("Created backup folder")

		i = 1
		for cf in changedFiles:
			backup.addFile(changedFiles[cf])
			logging.debug("Added file {} (processed {}/{} files)".format(changedFiles[cf].shortPath, i, len(changedFiles)))
			i += 1

		logging.debug("Added all files")

		backup.writeManifest(changedFiles, manifest)

		logging.debug("Wrote manifest")

		return backup
