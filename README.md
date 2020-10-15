# McBacky

*Minecraft Backup*

This is a backup system that only copies the files that changed since the last backup.

**WARNING**

I'm not 100% sure that this works. My code works (obviously :D) but I can't guarantee that the world that's restored from the backup is playable, not corrupted, or even correct. I know how special a minecraft world can be, and I would hate it if you trusted my software with it, for me to then fail you. With that said, there's no way the program will corrupt your original save file. So if youre curious you can use this system and test it, while you have another backups system to rely on - which is what I'm going to do to test this out.

## Background
Me and my friends servers tends to be big in size and active under a short period of time. Because of that there's no idea to create backups.

And you know where this is going... yeah, I do some fuckups and whoops some months work is annihilated.

### Solution
But if the parts of the world that noone has touched since the last backup didn't need to be backuped as well, the backups sizes would be much smaller, and backups can be done more regularly.

## Usage

### Install

	$ python setup.py install

### Make backup

	$ mcbacky [--backup-dir] [--compare] save-path

`backup-dir` is the directory in which each backup version will be stored, this will compare the `save-path` to the latest backup version. You can also select which version to compare to by setting `compare` to the name of a version. If you supply a full path to `compare` you can omit `backup-dir`.

### Restore
*Restoring has not been implemented but is easy to do*
