from os import listdir
from os.path import isdir,join
import numpy as np


def process_raw_midi_data(file_path):
	'''
	Read raw data from an already parsed text file from midi
	Convert the data table to numpy array and return
	'''
	
	# TODO: assert file_path is a path

	midi_data_table = []
	with open(file_path,'r') as midi_file:
		for line in midi_file:
			midi_data_table.append(line.rstrip().split(','))
	return np.array(midi_data_table,dtype=int)

def map_midi_power_to_percentage(midi_data_table,new_min=1,new_max=100):
	'''
	Maps the power to [new_min,new_max] (default to [1,100])
	Updates the midi_data_table and returns
	'''
	song_min = np.min(midi_data_table[:,5])
	song_max = np.max(midi_data_table[:,5])

	song_range = song_max - song_min
	new_range = new_max - new_min

	for i in range(len(midi_data_table)):
		orig_midi_power = midi_data_table[i][5]
		scaled_midi_power = float(orig_midi_power - song_min) / float(song_range)
		scaled_midi_power = float(new_min) + (scaled_midi_power * float(new_range))
		midi_data_table[i][5] = int(np.ceil(scaled_midi_power))

	return midi_data_table

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