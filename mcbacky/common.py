import hashlib
import string
import random
import os
import glob
import re

class File():
	def __init__(self, path):
		self.path = path

		self._fileHash = None

	def fileHash(self):
		if self._fileHash == None:
			chunkSize = 32768
			hasher = hashlib.md5()

			with open(self.path, "rb") as f:
				buf = f.read(chunkSize)

				while len(buf) > 0:
					hasher.update(buf)
					buf = f.read(chunkSize)

			self._fileHash = hasher.hexdigest()

		return self._fileHash

class WorldFile(File):
	def __init__(self, path, shortPath):
		super().__init__(path)

		self.shortPath = shortPath

class BackupFile(WorldFile):
	def __init__(self, path, shortPath, fileHash, backupName):
		super().__init__(path, shortPath)

		self._fileHash = fileHash
		self.backupName = backupName

	def fileHash(self):
		return self._fileHash

	def isFromBackup(self, name):
		return self.backupName == name

# https://stackoverflow.com/a/2030081
def randomString(length=5):
	letters = string.ascii_lowercase
	return "".join(random.choice(letters) for i in range(length))

def createNonCollidingName(name, d):
	"Adds a number to a file name if the desired name already exists"

	# If the desired path already exists
	if os.path.exists(d + name):
		# Find all files with the name with an extension "-(number)" in case this isn't the first time the
		# name collides
		files = glob.glob(d + name + "-[0-9]")

		# If there aren't any files that matches the name with the number extension that means that this is
		# the first time this name collides
		if len(files) == 0:
			n = 1
		else:
			# We want the highest number extension so sorting the names reversed will put that one in the first place
			files.sort(reverse=True)

			fileName = os.path.basename(files[0])
			# Match the name to groups
			match = re.match("^\\d{2}(\\d{2}_){4}\\d{2}-(\\d+)$", fileName)

			# Get the extension number and add 1
			n = int(match.group(2)) + 1

		# Add the number to the name that we now know is safe
		name += "-" + str(n)

	return name
