import setuptools
import os.path
import re

setuptools.setup(
	name="mcbacky",
	version="0.0.2",
	author="Anton Lindroth",
	author_email="ntoonio@gmail.com",
	license="MIT",
	description="Minecraft backup system",
	url="https://github.com/ntoonio/McBacky",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"OSI Approved :: GNU General Public License v3 (GPLv3)"
	],
    entry_points={
		"console_scripts": [
			"mcbacky = mcbacky.backup:main"
		]
	}
)
