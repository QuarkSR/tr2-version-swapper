import os, sys, shutil
from collections import namedtuple

#-------------------------------------------------------------------------------#
#---------------------------Environment checks----------------------------------#
#-------------------------------------------------------------------------------#

def WritePermissionsCheck():
	try:
		f = open("foo", "w")
		os.remove("foo")
	except OSError:
		InsufficientPermissions()
	finally:
		f.close()

def InsufficientPermissions():
	print("The script is unable to write files/folders.")
	print("You can try running it again with sudo as a workaround,")
	print("but most likely the problem is the game install location.")
	exit(1)

def MisplacedScript():
	print("It appears this script was not placed within a TR2 installation root.")
	print("This script should be in a folder called 'tr2-version-swapper' along")
	print("with all of the other folders in the archive.")
	ReinstallPrompt()

def MissingFolder(versionName):
	print(f"Could not find a {versionName} version folder with the script.")
	ReinstallPrompt()

def MissingFiles(file, version):
	print(f"Could not find {file} in the {version} folder!")
	ReinstallPrompt()

def MissingMusicFixFiles():
	print("Unfortunately, the music fix files are incomplete and thus cannot be")
	print("installed with this script right now. Your other files are fine.")
	ReinstallPrompt()

def ReinstallPrompt():
	print()
	print("You are advised to re-install the latest release to fix the issue:")
	print(data.install_link)
	exit(2)

#-------------------------------------------------------------------------------#
#--------------------------Variable setters-------------------------------------#
#-------------------------------------------------------------------------------#

def SetVariables(verbosity):
	if verbosity == "-v":
		verbose = True
		debug = False
	elif verbosity == "-d":
		verbose = True
		debug = True
	else:
		verbose = False
		debug = False

	git_link = "https://github.com/TombRunners/tr2-version-swapper"
	install_link = "https://github.com/TombRunners/tr2-version-swapper/releases/latest"

	version_names = ["Multipatch", "Eidos Premier Collection", "Eidos UK Box"]
	music_files = ["fmodex.dll", "winmm.dll"]

	# os.sep is equal to "\\" on windows platforms, and "/" on posix platforms
	# This ensures cross-platform compatibility.
	files = ["Tomb2.exe", f"data{os.sep}FLOATING.TR2", f"data{os.sep}TITLE.PCX",
			f"data{os.sep}TOMBPC.DAT"]

	patch_file = "Tomb2.exe"

	# Dynamically calculating these numbers for easier future growth.
	version_count = len(version_names)
	file_count = len(files)
	music_file_count = len(music_files)
	music_track_count = 61

	# construct new namedtuple
	Data = namedtuple("Data", """verbose debug git_link install_link
						version_names music_files files patch_file version_count
						file_count music_file_count, music_track_count""")

	# populate Data namedtuple with variables and make it globally accessible
	global data
	data = Data(verbose, debug, git_link, install_link, version_names,
			music_files, files, patch_file, version_count, file_count,
			music_file_count, music_track_count)

	return data

def SetDirectories():
	src = os.getcwd()
	music_fix = f"{src}{os.sep}utilities{os.sep}music_fix"
	patch_folder = f"{src}{os.sep}utilities{os.sep}patch"
	version_folders = []

	os.chdir("..")
	game_dir = os.getcwd()
	os.chdir(src)

	for i in data.version_names:
		version_folders.append(f"{src}{os.sep}versions{os.sep}{i}")

	Dirs = namedtuple("Dirs", "src music_fix patch_folder version_folders game_dir")
	global dirs
	dirs = Dirs(src, music_fix, patch_folder, version_folders, game_dir)

	return dirs

#-------------------------------------------------------------------------------#
#-------------------------Information printing----------------------------------#
#-------------------------------------------------------------------------------#

def PrintDirectories():
	print("Using the following directories:")
	print(f"Game: {dirs.game_dir}")
	print(f"Script: {dirs.src}")
	print(f"Music fix: {dirs.music_fix}")
	print(f"Patch: {dirs.patch_folder}")
	print()
	print("=== Versions ===")
	for i in data.version_names:
		print(i)

def PrintIntroduction():
	print("Welcome to the TR2 version swapper script!")
	print("This script's code can be viewed/edited with a text editor.")
	print("The official files with source control can be found here:")
	print(data.git_link)
	print()
	print("==== Notice ====")
	print("This batch script assumes the distributed folder containing it resides")
	print("in a fresh TR2 steam installation folder per the README. If installed")
	print("incorrectly, the script may refuse to work, or do worse by erroneously")
	print("proceeding if no problems are detected. Thus, it is asked that you be")
	print("sure to leave the script and the accompanying game files untouched.")
	print("================")
	print()
	return 0

def PrintMusicInfo():
	print("You switched to a non-Multipatch version. You may find that music no")
	print("longer works, or that the game lags when loading music. There is a")
	print("music fix available which should fix most music issues. You can learn")
	print("more on the Tomb Runner Discord server or speedrun.com/tr2.")
	print()

#-------------------------------------------------------------------------------#
#-------------------------Get user choices--------------------------------------#
#-------------------------------------------------------------------------------#

def GetSelectionIndex():
	choice = -1

	print("Enter the number of your desired version.")
	# Continuously loop until user chooses a valid number.
	while choice not in range(1, data.version_count+1):
		try:
			choice = int(input("> "))
		except ValueError:
			continue
	return data.version_names[choice-1]

def GetPatchInstallChoice():
	choice = -1

	print("(Optional) Install CORE's Patch 1? This is a separate EXE that is not required,")
	print("but may be used on top of English game versions. [0 = no, 1 = yes].")
	while choice not in range(2):
		try:
			choice = int(input("> "))
		except ValueError:
			continue
	return choice

def GetMusicInstallChoice():
	choice = -1

	print("Install the music fix? [0 = no, 1 = yes]")
	while choice not in range(2):
		try:
			choice = int(input("> "))
		except ValueError:
			continue
	return choice

#-------------------------------------------------------------------------------#
#------------------------Check files exist--------------------------------------#
#-------------------------------------------------------------------------------#

def CheckParentDirectoryFiles():
	for i in range(data.file_count):
		required_file = data.files[i]
		if data.debug:
			print(f"Looking for {required_file} in {dirs.game_dir}...")
		if not os.path.exists(f"{dirs.game_dir}{os.sep}{required_file}"):
			MisplacedScript()
		if data.debug:
			print()

def CheckVersionFoldersPresent():
	for i, j in enumerate(data.version_names):
		if data.debug:
			print(f"Looking for {j} in {dirs.game_dir}{os.sep}versions...")
		if not os.path.exists(dirs.version_folders[i]):
			MissingFolder(dirs.version_folders[i])
		if data.verbose:
			print()

def CheckMusicFiles(where):
	# Check the folder has all DLLs.
	for i in data.music_files:
		if data.debug:
			print(f"Looking for {i} in {where}..")
		if not os.path.exists(f"{where}{os.sep}{i}"):
			print(f"Music fix file not found in {where}.")
			return False
	# Check that the music folder has all music tracks.
	for i in range(1, data.music_track_count+1):
		# This f-string adds a leading 0 for one-digit numbers.
		track = f"{i:02d}.wma"
		if data.debug:
			print(f"Looking for music{os.sep}{track} in {where}..")
		if not os.path.exists(f"{where}{os.sep}music{os.sep}{track}"):
			print(f"Music fix file not found in {where}.")
			return False
	# If we haven't yet returned to the caller, the music fix must be present.
	return True

#-------------------------------------------------------------------------------#
#--------------------------------Main-------------------------------------------#
#-------------------------------------------------------------------------------#

def main():
	# Perform environment check and load variables.
	WritePermissionsCheck()
	data = SetVariables(sys.argv[-1])
	dirs = SetDirectories()

	CheckParentDirectoryFiles()
	CheckVersionFoldersPresent()
	
	if data.verbose:
		PrintDirectories()

	PrintIntroduction()

	# Get the user's version choice.
	print("Version list:")
	for i, j in enumerate(data.version_names, start=1):
		print(f"	{i}: {j}")

	selected_version = GetSelectionIndex()
	print(f"You selected: {selected_version}")
	print()

	# Check that the selected version folder has all the game files.
	for i in data.files:
		if data.verbose:
			print(f"Looking for {i} in {selected_version}...")
		if not os.path.exists(f"versions{os.sep}{selected_version}{os.sep}{i}"):
			MissingFiles(i, selected_version)
		if data.verbose:
			print()

	# Copy the game files
	os.remove(f"{dirs.game_dir}{os.sep}Tomb2.exe")
	os.remove(f"{dirs.game_dir}{os.sep}data{os.sep}FLOATING.TR2")
	os.remove(f"{dirs.game_dir}{os.sep}data{os.sep}TITLE.PCX")
	os.remove(f"{dirs.game_dir}{os.sep}data{os.sep}TOMBPC.DAT")

	shutil.copy(f"versions{os.sep}{selected_version}{os.sep}Tomb2.exe",
			f"{dirs.game_dir}{os.sep}Tomb2.exe")
	shutil.copy(f"versions{os.sep}{selected_version}{os.sep}data{os.sep}FLOATING.TR2",
			f"{dirs.game_dir}{os.sep}data{os.sep}FLOATING.TR2")
	shutil.copy(f"versions{os.sep}{selected_version}{os.sep}data{os.sep}TITLE.PCX",
			f"{dirs.game_dir}{os.sep}data{os.sep}TITLE.PCX")
	shutil.copy(f"versions{os.sep}{selected_version}{os.sep}data{os.sep}TOMBPC.DAT",
			f"{dirs.game_dir}{os.sep}data{os.sep}TOMBPC.DAT")

	print()
	print("=== Success ===")
	print(f"Version successfully swapped to {selected_version}")
	print("===============")
	print()

	# Copy the patch file if present and desired.
	patch = f"{dirs.patch_folder}{os.sep}{data.patch_file.lower()}"
	if data.debug:
		print(f"Looking for {patch}...")
	if not os.path.exists(patch):
		# We don't terminate here because the music fix can still be successfully
		# installed, even if the patch is not.
		print("Unfortunately, the patch file was not found and thus it cannot be")
		print("installed with this script right now. Your other files are fine.")
		print()
	else:
		install_patch = GetPatchInstallChoice()
		if install_patch == 1:
			shutil.copy(f"utilities/patch/tomb2.exe", f"{dirs.game_dir}{os.sep}Tomb2.exe")
			print()
			print("=== Success ===")
			print("Patch successfully installed.")
			print("===============")
			print()
		else:
			print("Skipping patch installation...")
			print()

	# Copy the music files if applicable and desired.
	if selected_version != "Multipatch":
		music_fix_already_installed = CheckMusicFiles(dirs.game_dir)
		if not music_fix_already_installed:
			PrintMusicInfo()

			music_fix_present = CheckMusicFiles(dirs.music_fix)
			if not music_fix_present:
				MissingMusicFixFiles()

			install_music_fix = GetMusicInstallChoice()
			if install_music_fix == 1:
				try:
					os.remove(f"{dirs.game_dir}{os.sep}fmodex.dll")
					os.remove(f"{dirs.game_dir}{os.sep}winmm.dll")
					for i in range(1, data.music_track_count+1):
						os.remove(f"{dirs.game_dir}{os.sep}music{os.sep}{i}.mp3")
						os.remove(f"{dirs.game_dir}{os.sep}music{os.sep}{i:02d}.wma")
				except FileNotFoundError:
					pass

				shutil.copy(f"utilities{os.sep}music_fix{os.sep}fmodex.dll",
						f"{dirs.game_dir}")
				shutil.copy(f"utilities{os.sep}music_fix{os.sep}winmm.dll",
						f"{dirs.game_dir}")
				for i in range(1, data.music_track_count+1):
					shutil.copy(f"utilities{os.sep}music_fix{os.sep}music{os.sep}{i:02d}.wma",
							f"{dirs.game_dir}{os.sep}music{os.sep}{i:02d}.wma")
				print()
				print("=== Success ===")
				print("Music fix successfully installed. No need to uninstall or")
				print("modify the relevant files for any future version switch.")
				print("===============")
				print()
			else:
				print("Skipping music fix installation...")
		else:
			print("The music fix appears to be already installed.")
			print()

	print("Run this script again anytime you wish to change or patch the version.")
	exit(0)

if __name__ == "__main__":
	main()
