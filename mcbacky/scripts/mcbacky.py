import argparse
import sys
import os
import logging

from mcbacky.world import World
from mcbacky.backup import BackupHistory, Backup
from mcbacky.scripts.formatter import CustomLoggerFormatter

def action_save(args):
	worldPath = args.world_path.rstrip("/")
	backupPath = os.path.abspath(args.backup_path).rstrip("/")

	logging.info("world_path\t{}".format(worldPath))
	logging.info("backup_path\t{}".format(backupPath))

	if not os.path.exists(worldPath + "/" + "level.dat"):
		return "The given path doesn't seems to be a Minecraft world (no level.dat)\n - Path: " + worldPath

	if not os.path.exists(backupPath):
		return "The backup path doesn't exist.\n - Path: " + backupPath

	isBukkit = os.path.isdir(worldPath + "_nether") and os.path.isdir(worldPath + "_the_end") and not os.path.exists(worldPath + "/DIM-1") and not os.path.exists(worldPath + "/DIM1")

	logging.info("World is " + ("" if isBukkit else "not ") + "using the bukkit world structure")

	world = World(worldPath, backupPath, isBukkit)

	if args.dry:
		changedFiles = world.generateManifest()[0]

		if len(changedFiles) == 0:
			return "No files has been changed"

		logging.info("Files that has been changed:\n{}".format("\n".join(["- " + x for x in changedFiles])))

		return "Didn't create a backup because of the --dry flag"

	backup = world.makeBackup()

	if backup == False:
		return "No changed files to create backup of"

	logging.info("Files that has been changed:\n{}".format("\n".join(["- " + x.shortPath for x in backup.getManifest() if x.changedInBackup(backup.name)])))

	return "Created backup '{}'".format(backup.name)

def action_restore(args):
	if Backup.isBackup(args.backup_path):
		backup = Backup(args.backup_path)
	else:
		backups = BackupHistory(args.backup_path)

		backupVersions = backups.listBackups(False)

		if len(backupVersions) == 0:
			return "The path is neither a backup or a folder containing backup versions"
		elif len(backupVersions) == 1:
			backup = backupVersions[0]
		else:
			print("Choose one of the available backups in the directory")
			for b in backupVersions:
				print("-", b.name)

			backupVersion = input("> ")
			backupPath = backups.path + "/" + backupVersion

			if Backup.isBackup(backupPath):
				backup = Backup(backupPath)
			else:
				return "That backup doesn't exist"

	files, path = backup.restore(args.restore_dir)

	logging.info("The following files are contained in the new restoration\n{}".format("\n".join(["- Copied '{}' from '{}'".format(f.shortPath, f.backupName) for f in files])))

	return "Created restoration at {}".format(path)

def runAction(args):
	# Setup the logger
	fh = logging.FileHandler(os.path.expanduser("~/.mcbacky.log"))
	ch = logging.StreamHandler()
	fh.setFormatter(CustomLoggerFormatter(True))
	ch.setFormatter(CustomLoggerFormatter())
	fh.level = 10
	ch.level = 10 if args.debug else 20 if args.verbose else 25
	logging.basicConfig(handlers=[fh, ch], level=0)
	logging.addLevelName(25, "INFO")

	if args.action == "save":
		return action_save(args)
	elif args.action == "restore":
		return action_restore(args)
	else:
		return "No such action '{}' found".format(args.action)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbose", action="store_true", help="print the files that are copied")
	parser.add_argument("--debug", action="store_true", help="print debug logs")
	parser.add_argument("-d", "--dry", action="store_true", help="don't do anything, just print the file names")

	subparsers = parser.add_subparsers(title="action", dest="action")
	subparsers.required = True

	saveParser = subparsers.add_parser("save")
	saveParser.add_argument("world_path", nargs="?", default=os.getcwd(), type=str)
	saveParser.add_argument("backup_path", type=str)

	restoreParser = subparsers.add_parser("restore")
	restoreParser.add_argument("backup_path", type=str)
	restoreParser.add_argument("restore_dir", nargs="?", default=os.getcwd(), type=str)

	args = parser.parse_args()

	result = runAction(args)
	logging.log(25, result)
