import hashlib
import os
import pathlib
import glob
import zipfile
from datetime import datetime
import shutil
import re
import argparse
import sys

class Save():
	def __init__(self, path):
		"""
		savePath: absolute path to the folder containing level.dat
		"""

		self.path = pathlib.Path(path)
		self.checksumCache = {}

		if not self.path.exists() or not self.path.is_dir():
			raise Exception("savePath is not a directory")

		self.worldName = os.path.basename(self.path)

	def contentFiles(self):
		for path in glob.iglob(str(self.path) + "/**/*", recursive=True):
			path = pathlib.Path(path)

			if path.is_dir():
				continue

			yield os.path.relpath(path, self.path)

	def countContentFiles(self):
		return len(glob.glob(str(self.path) + "/**/*", recursive=True))

	def fileAbsolutePath(self, f):
		return os.path.join(self.path, f)

	def checksum(self, f):
		if f in self.checksumCache:
			return self.checksumCache[f]

		hashMd5 = hashlib.md5()

		with open(self.path / f, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hashMd5.update(chunk)

		cs = hashMd5.hexdigest()
		self.checksumCache[f] = cs

		return cs

class Backup():
	def __init__(self, path):
		"""
		path: the directory that backup versions will be created in
		"""

		self.path = path

		if not path.exists() or not path.is_dir():
			raise Exception("path is not a directory")

	def latestVersionName(self):
		s = max(glob.iglob(str(self.path.absolute()) + "/*"))

		if s.endswith(".zip"):
			s = s[:-len(".zip")]

		return os.path.relpath(s, self.path)

class BackupVersion():
	def __init__(self, backup, name=None):
		"""
		backup: the backup object that contains other backup versions
		name: the name of the backup version, leave to None when creating a new
		"""

		self.backup = backup
		self.name = name
		self.path = None
		self.zipped = False
		self.newVersion = True
		self.manifestFile = None
		self.manifest = {}

		if self.name:
			self.newVersion = False

			if (self.backup.path / (self.name + ".zip")).exists() and not (self.backup.path / (self.name + ".zip")).is_dir(): # If zip-version exists and is a file
				self.zipped = True
				self.path = self.backup.path / (self.name + ".zip")
			elif not (self.backup.path / self.name).exists() or not (self.backup.path / self.name).is_dir(): # If the folder exists and is a dir
				raise Exception("backup version doesn't exist in the backup dir")

	def create(self):
		if self.name != None:
			raise Exception("name is not None, which propably means that this version already exists")

		# Create a name based on the date with a sufix, if that exists: increase the sufix

		nameSuggestion = datetime.now().strftime("%Y-%m-%d") + "-"
		collidingNames = glob.glob(str(self.backup.path.absolute()) + "/" + nameSuggestion + "*")

		# I don't know why i keep making these... they're just too satisfying... it calulates the sufix
		sufix = "0" if len(collidingNames) == 0 else str(max([int(re.match(r"(?:\d{4}-\d{2}-\d{2}-)(\d+)?(?:\.zip)?", os.path.relpath(n, self.backup.path)).group(1)) for n in collidingNames]) + 1)

		self.name = nameSuggestion + sufix
		self.path = self.backup.path / self.name

		print(" | Creating backup version:", self.path)

		os.makedirs(self.path)
		self.manifestFile = open(self.path / "manifest.txt", "w")

	def finalize(self):
		if self.zipped:
			raise Exception("trying to finalize a version that already is zip")

		self.manifestFile.close()

		with zipfile.ZipFile(self.backup.path / (self.name + ".zip"), "w") as zipObj:
			for filePath in glob.iglob(str(self.path) + "/**/*", recursive=True):
				f = os.path.relpath(pathlib.Path(filePath), self.path)
				zipObj.write(filePath, f)

		shutil.rmtree(self.path)

		self.zipped = True
		self.path = pathlib.Path(str(self.path) + ".zip")

	def readManifest(self):
		if self.newVersion: raise Exception("trying to use a function that only is available if the BackupVersion is not new")

		with zipfile.ZipFile(self.path) as z:
			data = z.read("manifest.txt").decode("utf-8")
			self.manifest = {}

			for line in data.split("\n"):
				parts = line.strip().split(";")

				if len(parts) != 3:
					continue

				self.manifest[parts[2]] = parts[0:2]

	def shouldBackup(self, f, save):
		if len(self.manifest) == 0:
			self.readManifest()

		return f not in self.manifest or save.checksum(f) != self.manifest[f][0]

	def addToBackup(self, f, save):
		origPath = save.path / f
		newPath = self.path / f

		os.makedirs(os.path.dirname(newPath), exist_ok=True)
		shutil.copyfile(origPath, newPath)

		self.writeToManifest(f, save.checksum(f), self.name)

	def writeToManifest(self, f, checksum, version):
		if self.zipped and not self.newVersion:
			raise Exception("trying to use a function that only is available if the version is now and hasn't been zipped")

		self.manifestFile.write(";".join([checksum, version, f]) + "\n")

def runBackup(save, backup, compareVersion, threshold=10):
	newBackupVersion = BackupVersion(backup)
	newBackupVersion.create()

	changedFiles = 0
	totalFiles = save.countContentFiles()

	for f in save.contentFiles():
		if compareVersion.shouldBackup(f, save):
			# TODO: do not copy data-pack if thats chosen

			newBackupVersion.addToBackup(f, save)

			changedFiles += 1
		else:
			newBackupVersion.writeToManifest(f, *compareVersion.manifest[f])

	newBackupVersion.finalize()

	if threshold < changedFiles:
		print("Did not reach threshold ... removing new backup")
		os.remove(newBackupVersion.path)
	else:
		print("Backed up", changedFiles, "changed files, out of", totalFiles, "total files")

def main():
	print(" ! Before running this you should make sure that the world won't be written to during backup.\n ! This can be done by exiting if it's on singleplayer, stopping the server, or running /save-off. Remember to do /save-on when the backup is done\n")

	parser = argparse.ArgumentParser()
	parser.add_argument("--save-path", "-p", type=pathlib.Path, required=True, dest="savePath", help="path to the world folder you want to backup")
	parser.add_argument("--backup-dir", "-b", type=pathlib.Path, dest="backupDir", help="the directory that old versions are in and the new will be created in")
	parser.add_argument("--compare", "-c", help="name of or path to the version to compare to, the new version will be created as a sibling. Should not be a path")
	parser.add_argument("--threshold", "-t", type=int, default=10, help="don't create a new backup version unless this many files has changed")
	# TODO: add flag controlling wheter data-packs should be in the backup or not

	args = parser.parse_args()

	# Make sure we have enough information
	if args.backupDir == None and (args.compare == None or not os.path.isabs(args.compare)):
		parser.error("Either --backup-dir or --compare needs to be set. If only --compare is set it has to be an absolute path")

	if args.threshold < 1:
		parser.error("Threshold can't be lower than 1")

	# Extract the information and set up objects

	save = Save(args.savePath)
	backup = None
	compareVersion = None

	if args.backupDir != None:
		backup = Backup(args.backupDir)
	else:
		backup = Backup(pathlib.Path(args.compare).parent)

	if args.compare != None:
		if os.path.isabs(args.compare):
			compareVersionName = os.path.basename(args.compare)
		else:
			compareVersionName = args.compare

		compareVersion = BackupVersion(backup, compareVersionName)
	else:
		compareVersion = BackupVersion(backup, backup.latestVersionName())

	# Show some information
	print(" | Creating a backup of:", save.path)
	print(" | Backup to be stored in:", backup.path)
	print(" | Comparing to:", compareVersion.path)

	# Run the backup
	runBackup(save, backup, compareVersion, args.threshold)

if __name__ == "__main__":
	main()