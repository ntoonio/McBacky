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

	$ mcbacky [--dry] [--verbose] save [save_path] {backup_path}

Without setting `save_path` it will have the value of the current work directory.

**Example:**

	$ mcbacky save .../server/world .../backups/my_server_world

### Restore

	$ mcbacky [--dry] [--verbose] restore [backup_path] [version]

- Default value for `backup_path` is the current working directory.
- Default value for `version` is `"latest"`

**Example:**

	$ mcbacky restore .../backups/my_server_world 2020_01_22_19_03
