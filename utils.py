from os import listdir
from os.path import isdir,join
import numpy as np


def process_raw_midi_data(file_path):
	'''
	Read raw data from an already parsed text file from midi
	Convert the data table to numpy array and return
	'''
	
	# TODO: assert file_path is a path
	# TODO: if row_data[3] == 3 and row_data[4] != 64
	# TODO: ignore row_data[1] (combine different channels)


	midi_data_table = []
	with open(file_path,'r') as midi_file:
		for line in midi_file:
			midi_data_table.append(line.rstrip().split(','))
	return np.array(midi_data_table,dtype=int)

def translate_into_percentage(value,old_min,old_max):
	'''
	Translate and return a value to be a percentage [1,100]
	'''
	old_range = old_max - old_min

	percentage = (float(value) - float(old_min)) / float(old_range) * 100.0

	return percentage


def map_midi_to_percentage(midi_data_table):
	'''
	Maps the power to [new_min,new_max] (default to [1,100])
	Updates the midi_data_table and returns
	'''

	# <Time, track number, MIDI channel, type, key, value>
	# if type = 0 then it's a note off
	# also if value = 0 it's a note off too

	# TODO: detect if note if off
	# Skips all note off and skip all sustains
	song_with_only_note_on = np.array([row for row in midi_data_table \
									      if (row[5] > 0 and row[3] > 0) \
									      and (row[3] != 3 and row[4] != 64)])
	# TODO: exclude 0 when getting np.min
	song_min = np.min(song_with_only_note_on[:,5])
	song_max = np.max(song_with_only_note_on[:,5])

	for i in range(len(midi_data_table)):
		# TODO: append a note of 0 if note power is 0
		if midi_data_table[i][5] > 0 and midi_data_table[i][3] > 0 and \
		   midi_data_table[i][3] != 3 and midi_data_table[i][3] != 64:
			orig_power = midi_data_table[i][5]
			power_percentage = translate_into_percentage(orig_power,song_min,song_max)
			midi_data_table[i][5] = power_percentage
			
	return midi_data_table

def read_profile(profile_path):
	'''
	Reads the profiles in profile_path and returns a dictionary
	profile = {'sustain'|'no_sustain':[note,low_normal_percentage,high_normal_percentage]}
	'''

	# TODO: assert file_path is a path

	profile = {}
	profile['sustain'] = []
	profile['no_sustain'] = []

	num_notes_in_profile = 84

	with open(profile_path+'/high.cfg','r') as high, \
		 open(profile_path+'/low_no_sus.cfg','r') as low_no_sus, \
		 open(profile_path+'/low_sus.cfg','r') as low_sus:

		high_normal_percentagentent = [line.strip('\n').split(',') for line in high.readlines()]
		low_no_sus_content = [line.strip('\n').split(',') for line in low_no_sus.readlines()]
		low_sus_content = [line.strip('\n').split(',') for line in low_sus.readlines()]

		for i in range(len(high_content)):
			profile['sustain'].append([i+1,low_sus_content[i][3], high_content[i][3]])
			profile['no_sustain'].append([i+1,low_no_sus_content[i][3],high_content[i][3]])

		profile['sustain'] = np.array(profile['sustain'],dtype=int)
		profile['no_sustain'] = np.array(profile['no_sustain'],dtype=int)

	return profile

def apply_profile(profile,new_min=1,new_max=100):
	'''
	map profile's power to percentage
	'''
	for key in profile.keys():
		for i in range(len(profile[key])):
			low_normal_power = profile[key][i][1]
			high_normal_power = profile[key][i][2]
			profile[key][i][1] = translate_into_percentage(low_normal_power,low_normal_power,high_normal_power)
			profile[key][i][2] = translate_into_percentage(high_normal_power,low_normal_power,high_normal_power)

	return profile


