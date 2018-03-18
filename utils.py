from os import listdir
from os.path import isdir,join
import numpy as np
import pandas as pd
import const


def filter_raw_data(file_path):
	'''
	Read raw data from an already parsed text file from midi
	Convert and filter the data table to numpy array and return
	'''
	
	# TODO: assert file_path is a path
	# TODO: if row_data[3] == 3 and row_data[4] != 64

	dataframe = pd.read_csv(file_path)

	mask = dataframe.event == 0
	column_name = 'power'
	dataframe.loc[mask,column_name] = 0

	return dataframe


# def add_id(data):
# 	data = np.insert(data,0,0,axis=1)
# 	for i in range(len(data)):
# 		data[i][0] = i+1
# 	return data

# TODO
def detect_sustain():
	pass

def add_sustain_column(dataframe):

	# add a column of zeroes in data
	dataframe['sustain'] = pd.Series(np.zeros(dataframe.shape[0],dtype=int),index=dataframe.index)

	# detect sustain
	sustain_flag = False
	for index,row in dataframe.iterrows():
		if row['event'] == 3 and row['note'] == 64:
			if row['power'] > 0:
				sustain_flag = True
			else:
				sustain_flag = False
			continue
		if row['event'] == 1 and row['power'] > 0:
			dataframe.loc[index]['sustain'] = 1 if sustain_flag == True else 0

	return dataframe

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
	song_with_only_note_on = np.array([row for row in midi_data_table if row[4] == 1])
	# TODO: exclude 0 when getting np.min
	song_min = np.min(song_with_only_note_on[:,6])
	song_max = np.max(song_with_only_note_on[:,6])

	for i in range(len(midi_data_table)):
		if midi_data_table[i][4] == 1:
			orig_power = midi_data_table[i][6]
			power_percentage = translate_into_percentage(orig_power,song_min,song_max,const.SONG_BOUNDARY)
			midi_data_table[i][6] = power_percentage
			
	return midi_data_table

def read_profile(profile_path):
	'''
	Reads the profiles in profile_path and returns a dictionary
	profile = {'sustain'|'no_sustain':[note,low_normal_percentage,high_normal_percentage]}
	[note,(high_power_min,high_power_max),(high_dur_min,high_dur_max),(normal_power_min,normal_power_max),(normal_dur_min,normal_power_max),(low_power_min,low_power_max)]
	'''

	# TODO: assert file_path is a path

	profile = {}

	num_notes_in_profile = 84

	with open(profile_path+'/loud.cfg','r') as loud, \
		 open(profile_path+'/quiet_no_sus.cfg','r') as quiet_no_sus, \
		 open(profile_path+'/quiet_sus.cfg','r') as quiet_sus:

		loud_content = [line.strip('\n').split(',') for line in loud.readlines()]
		quiet_no_sus_content = [line.strip('\n').split(',') for line in quiet_no_sus.readlines()]
		quiet_sus_content = [line.strip('\n').split(',') for line in quiet_sus.readlines()]


		profile['sustain'] = np.copy(loud_content)
		profile['no_sustain'] = np.copy(loud_content)

	for i in range(len(loud_content)):
		note = i + 1

		# profile['sustain'][,:1] = (loud_content[,:1],quiet_sus[,:1])
		# profile['no_sustain'][,:1] = (loud_content[,:1],quiet_no_sus[,:1])

		sus_row = [(loud,quiet_sus) for loud,quiet_sus in zip(loud_content[i],quiet_sus_content[i])]
		print (sus_row)


		no_sus_row = [(loud,quiet_no_sus) for loud,quiet_no_sus in zip(loud_content[i],quiet_no_sus_content[i])]
		print (no_sus_row)

		# high power & dur
		high_power_range = (high_power_min,high_max) = (1,3)
		high_dur_range = (high_dur_min,high_dur_max) = (1,3)

		# normal power & dur
		normal_power_range = (normal_power_min, nomral_power_max) = (1,3)
		normal_dur_range = (normal_dur_min, normal_dur_max) = (1,3)

		# low power
		low_power_range = (low_power_min, low_power_max) = (1,3)

		# profile['sustain'].append([i+1,low_sus_content[i][3], high_content[i][3]])
		# profile['no_sustain'].append([i+1,low_no_sus_content[i][3],high_content[i][3]])

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
		if row[4] == 1:
			note = row[5]
			low_normal_power = profile['sustain'][note][1] if row[7] == 1 else \
							   profile['no_sustain'][note][1]
			high_normal_power = profile['sustain'][note][2] if row[7] == 1 else \
								profile['no_sustain'][note][2]
			power_range = high_normal_power - low_normal_power
			note_percentage = row[6]
			row[6] = low_normal_power + power_range * note_percentage / 100
	return data

def sort_by_note(data):
	data = sorted(data, key = lambda x: (x[5],x[1]))
	return np.array(data,dtype=int)
