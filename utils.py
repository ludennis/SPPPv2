from os import listdir
from os.path import isdir,join


def process_raw_midi_data(file_path):

	# TODO: assert file_path is a path

	raw_midi_data_table = []
	with open(file_path,'r') as midi_file:
		for line in midi_file:
			raw_midi_data_table.append(line.rstrip().split(','))
	return raw_midi_data_table

def read_profiles(profile_path):

	# TODO: assert file_path is a path

	profiles = {}
	if isdir(profile_path):
		for file_name in listdir(profile_path):
			file_path = join(profile_path,file_name)
			print (file_path)
			with open(file_path,'r') as file:
				profiles[file_name] = []
				for line in file:
					profiles[file_name].append(line.rstrip().split(','))
	return profiles