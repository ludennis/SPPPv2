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

def translate_into_new_range(value,old_min,old_max,new_min,new_max):
	'''
	Translate and return a value to be in a new range
	'''

	old_range = old_max - old_min
	new_range = new_max - new_min

	value = (float(value) - float(old_min)) / float(old_range)
	value = float(new_min) + float(value) * float(new_range)

	return np.ceil(value)


def map_midi_power_to_percentage(midi_data_table,new_min=1,new_max=100):
	'''
	Maps the power to [new_min,new_max] (default to [1,100])
	Updates the midi_data_table and returns
	'''
	song_min = np.min(midi_data_table[:,5])
	song_max = np.max(midi_data_table[:,5])

	for i in range(len(midi_data_table)):
		orig_power = midi_data_table[i][5]
		mapped_power = translate_into_new_range(orig_power,song_min,song_max,new_min,new_max)
		midi_data_table[i][5] = int(mapped_power)
		
	return midi_data_table

def process_profile(profile_path):
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

		high_content = [line.strip('\n').split(',') for line in high.readlines()]
		low_no_sus_content = [line.strip('\n').split(',') for line in low_no_sus.readlines()]
		low_sus_content = [line.strip('\n').split(',') for line in low_sus.readlines()]

		for i in range(len(high_content)):
			profile['sustain'].append([i+1,low_sus_content[i][3], high_content[i][3]])
			profile['no_sustain'].append([i+1,low_no_sus_content[i][3],high_content[i][3]])

		profile['sustain'] = np.array(profile['sustain'],dtype=int)
		profile['no_sustain'] = np.array(profile['no_sustain'],dtype=int)

	return profile

def percentage_from_profile(data_table, profiles):

	# TODO: assert there are 3 profiles
	# TODO: assert each profile has 84 keys


	# Sustain is on when input is <0,0,0,3,64,x> , where x can be 1-128
	# Sustain is off when input is <0,0,0,3,64,0>

	sustain_flag = False

	for i in range(data_table):
		row_data = data_table[i]
		if row_data[3] == 3 and row_data[4]:
			sustain_flag = True if row_data[5] > 0 else False
			continue
		note = row_data[4]
		low_normal_power = profiles['low_sus.cfg'][note][3] if sustain_flag \
						   else profiles['low_no_sus.cfg'][note][3]
		high_normal_power = profiles['high.cfg'][note][3]



