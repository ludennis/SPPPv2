from os import listdir
from os.path import isdir,join
import numpy as np
import const


def filter_raw_data(file_path):
	'''
	Read raw data from an already parsed text file from midi
	Convert and filter the data table to numpy array and return
	'''
	
	# TODO: assert file_path is a path
	# TODO: if row_data[3] == 3 and row_data[4] != 64

	midi_data_table = []
	with open(file_path,'r') as midi_file:
		for line in midi_file:
			midi_data_table.append(line.rstrip().split(','))

	# convert to numpy array first
	midi_data_table = np.array(midi_data_table,dtype=int)

	# TODO: change power to noteoff to 0
	for i in range(len(midi_data_table)):
		if midi_data_table[i][3] == 0: midi_data_table[i][5] = 0

	return np.array(midi_data_table,dtype=int)


# TODO
def detect_sustain():
	pass

def add_sustain_column(data):
	# add a column of zeroes in data
	data = np.insert(data,data.shape[1],0,axis=1)

	# detect sustain
	sustain_flag = False
	for row in data:
		if row[3] == 3 and row[4] == 64:
			if row[5] > 0:
				sustain_flag = True
			else:
				sustain_flag = False
			continue
		if row[3] == 1 and row[5] > 0:
			row[6] = 1 if sustain_flag == True else 0

	return data

def translate_into_percentage(value,old_min,old_max,song_range=(0,100)):
	'''
	Translate and return a value to be a percentage [1,100]
	'''

	old_range = old_max - old_min
	new_range = song_range[1] - song_range[0]
	new_min = song_range[0]

	assert old_range > 0, 'translate_into_percentage(): old_range is less than or equal 0'
	assert new_range > 0, 'translate_into_percentage(): new_range is less than or equal 0'

	percentage = (((value - old_min) * new_range) / (old_range)) + new_min

	return percentage

def map_midi_to_percentage(midi_data_table):
	'''
	Maps the power to [new_min,new_max] (default to [1,100])
	Updates the midi_data_table and returns
	'''

	# <Time, track number, MIDI channel, type, key, value>
	# if type = 0 then it's a note off
	# also if value = 0 it's a note off too

	# TODO: only have note ons
	song_with_only_note_on = np.array([row for row in midi_data_table if row[3] == 1])
	# TODO: exclude 0 when getting np.min
	song_min = np.min(song_with_only_note_on[:,5])
	song_max = np.max(song_with_only_note_on[:,5])

	for i in range(len(midi_data_table)):
		if midi_data_table[i][3] == 1:
			orig_power = midi_data_table[i][5]
			power_percentage = translate_into_percentage(orig_power,song_min,song_max,const.SONG_BOUNDARY)
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

	with open(profile_path+'/loud.cfg','r') as high, \
		 open(profile_path+'/quiet_no_sus.cfg','r') as low_no_sus, \
		 open(profile_path+'/quiet_sus.cfg','r') as low_sus:

		high_content = [line.strip('\n').split(',') for line in high.readlines()]
		low_no_sus_content = [line.strip('\n').split(',') for line in low_no_sus.readlines()]
		low_sus_content = [line.strip('\n').split(',') for line in low_sus.readlines()]

		for i in range(len(high_content)):
			profile['sustain'].append([i+1,low_sus_content[i][3], high_content[i][3]])
			profile['no_sustain'].append([i+1,low_no_sus_content[i][3],high_content[i][3]])

		profile['sustain'] = np.array(profile['sustain'],dtype=int)
		profile['no_sustain'] = np.array(profile['no_sustain'],dtype=int)

	return profile

def apply_profile(data,profile):
	'''
	map profile's power to percentage
	'''
	#  [16300     0     0     1    50    50     1]

	# profile['sustain'] => [note,low,high] => [ 50, 108, 143]
	# profile['no_sustain'] => [note,low,high] => [ 50, 113, 143]

	for row in data:
		if row[3] == 1:
			note = row[4]
			low_normal_power = profile['sustain'][note][1] if row[6] == 1 else \
							   profile['no_sustain'][note][1]
			high_normal_power = profile['sustain'][note][2] if row[6] == 1 else \
								profile['no_sustain'][note][2]
			power_range = high_normal_power - low_normal_power
			note_percentage = row[5]
			row[5] = low_normal_power + power_range * note_percentage / 100
	return data

def sort_by_note(data):
	data = sorted(data, key = lambda x: (x[4],x[0]))
	return np.array(data,dtype=int)
