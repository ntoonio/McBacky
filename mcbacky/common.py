import hashlib
import string
import random

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

# https://stackoverflow.com/a/2030081
def randomString(length=5):
	letters = string.ascii_lowercase
	return "".join(random.choice(letters) for i in range(length))
