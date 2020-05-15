import argparse
import sys
import os

from McBacky import save
from McBacky import restore

def action_save(args):
	savePath = args.save_path.rstrip("/")
	backupPath = os.path.abspath(args.backup_path).rstrip("/")

	if args.dry and args.verbose:
		print("save_path\t", savePath)
		print("backup_path\t", backupPath)

	if not os.path.exists(savePath + "/" + "level.dat"):
		return "The given path doesn't seems to be a Minecraft world (no level.dat)\n - Path: " + savePath

	if not os.path.exists(backupPath):
		return "The backup path doesn't exist.\n - Path: " + backupPath

	s = save.Save(
		savePath,
		backupPath
	)

	changedFiles, timeMark = s.createBackup(dryRun=args.dry)

	if len(changedFiles) == 0:
		return "No changed files to create backup of"

	if args.verbose and not args.dry:
		print("Files that were copied:")

		for f in changedFiles: print(" - " + f)

	elif args.dry:
		print("Files that would have been copied:")

		for f in changedFiles: print(" - " + f)

		return "Would have created backup version with id '{}'".format(timeMark)

	return "Created backup version with id '{}'".format(timeMark)

def action_restore(args):
	pass

def runAction(args):
	if args.action == "save":
		return action_save(args)
	elif args.action == "restore":
		return action_restore(args)
	else:
		return "No such action found"

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbose", action="store_true", help="print the files that are copied")
	parser.add_argument("-d", "--dry", action="store_true", help="don't do anything, just print the file names")

	subparsers = parser.add_subparsers(title="action", dest="action")
	subparsers.required = True

	saveParser = subparsers.add_parser("save")
	saveParser.add_argument("save_path", nargs="?", default=os.getcwd(), type=str)
	saveParser.add_argument("backup_path", type=str)

	restoreParser = subparsers.add_parser("restore")
	restoreParser.add_argument("backup_path", type=str)

	args = parser.parse_args()

	print(runAction(args))
