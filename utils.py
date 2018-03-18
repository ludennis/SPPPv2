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

	df = pd.read_csv(file_path)

	mask = df.event == 0
	column_name = 'power'
	df.loc[mask,column_name] = 0

	return df

# TODO
def detect_sustain():
	pass

def add_sustain_column(df):
	'''
	add a sustain column to the table for each note on
	'''
	# add a column of zeroes in data
	df['sustain'] = pd.Series(np.zeros(df.shape[0],dtype=int),index=df.index)

	# detect sustain
	sustain_flag = False
	for index,row in df.iterrows():
		if row['event'] == 3 and row['note'] == 64:
			if row['power'] > 0:
				sustain_flag = True
			else:
				sustain_flag = False
			continue
		if row['event'] == 1 and row['power'] > 0:
			df.loc[index]['sustain'] = 1 if sustain_flag == True else 0

	return df

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

def map_midi_to_percentage(df):
	'''
	Maps the power to [new_min,new_max] (default to [1,100])
	Updates the midi_data_table and returns
	'''

	# <Time, track number, MIDI channel, type, key, value>
	# if type = 0 then it's a note off
	# also if value = 0 it's a note off too

	# TODO: only have note ons
	song_with_only_note_on = df.loc[df['event']==1]
	# song_with_only_note_on = np.array([row for row in df if row[4] == 1])
	# TODO: exclude 0 when getting np.min
	song_min = song_with_only_note_on['power'].min()
	song_max = song_with_only_note_on['power'].max()

	for index,row in df.iterrows():
		if row['event'] == 1:
			orig_power = row['power']
			power_percentage = translate_into_percentage(orig_power,song_min,song_max,const.SONG_BOUNDARY)
			df.loc[index]['power'] = power_percentage
			
	return df

def read_profile(profile_path):
	'''
	Reads the profiles in profile_path and returns a dictionary
	profile = {'sustain'|'no_sustain':[note,low_normal_percentage,high_normal_percentage]}
	[note,(high_power_min,high_power_max),(high_dur_min,high_dur_max),(normal_power_min,normal_power_max),(normal_dur_min,normal_power_max),(low_power_min,low_power_max)]
	'''

	# TODO: assert file_path is a path

	profile = {}

	num_notes_in_profile = 84

	loud_df = pd.read_csv(profile_path+'/loud.csv')
	quiet_no_sus_df = pd.read_csv(profile_path+'/quiet_no_sus.csv')
	quiet_sus_df = pd.read_csv(profile_path+'/quiet_sus.csv')

	# merge loud and quiet_sus according to index
	merge_df = loud_df.merge(quiet_sus_df,right_index=True,left_index=True)
	sustain_df = pd.DataFrame(columns=['note','high_power_min','high_power_max','high_dur_min','high_dur_max',\
									   'normal_power_min','normal_power_max','normal_dur_min','normal_dur_max',\
									   'low_power_min','low_power_max','low_dur_min','low_dur_max'])
	
	sustain_df['note'] = merge_df['note_x']
	sustain_df['high_power_min'] = merge_df[['high_power_x','high_power_y']].min(axis=1)
	sustain_df['high_power_max'] = merge_df[['high_power_x','high_power_y']].max(axis=1)
	sustain_df['high_dur_min'] = merge_df[['high_dur_x','high_dur_y']].min(axis=1)
	sustain_df['high_dur_max'] = merge_df[['high_dur_x','high_dur_y']].max(axis=1)
	sustain_df['normal_power_min'] = merge_df[['normal_power_x','normal_power_y']].min(axis=1)
	sustain_df['normal_power_max'] = merge_df[['normal_power_x','normal_power_y']].max(axis=1)
	sustain_df['normal_dur_min'] = merge_df[['normal_dur_x','normal_dur_y']].min(axis=1)
	sustain_df['normal_dur_max'] = merge_df[['normal_dur_x','normal_dur_y']].max(axis=1)
	sustain_df['low_power_min'] = merge_df[['low_power_x','low_power_y']].min(axis=1)
	sustain_df['low_power_max'] = merge_df[['low_power_x','low_power_y']].max(axis=1)
	sustain_df['low_dur_min'] = merge_df[['low_dur_x','low_dur_y']].min(axis=1)
	sustain_df['low_dur_max'] = merge_df[['low_dur_x','low_dur_y']].max(axis=1)

	# merge loud and quiet_no_sus according to index
	merge_df = loud_df.merge(quiet_no_sus_df,right_index=True,left_index=True)
	no_sustain_df = pd.DataFrame(columns=['note','high_power_min','high_power_max','high_dur_min','high_dur_max',\
									      'normal_power_min','normal_power_max','normal_dur_min','normal_dur_max',\
									      'low_power_min','low_power_max','low_dur_min','low_dur_max'])

	no_sustain_df['note'] = merge_df['note_x']
	no_sustain_df['high_power_min'] = merge_df[['high_power_x','high_power_y']].min(axis=1)
	no_sustain_df['high_power_max'] = merge_df[['high_power_x','high_power_y']].max(axis=1)
	no_sustain_df['high_dur_min'] = merge_df[['high_dur_x','high_dur_y']].min(axis=1)
	no_sustain_df['high_dur_max'] = merge_df[['high_dur_x','high_dur_y']].max(axis=1)
	no_sustain_df['normal_power_min'] = merge_df[['normal_power_x','normal_power_y']].min(axis=1)
	no_sustain_df['normal_power_max'] = merge_df[['normal_power_x','normal_power_y']].max(axis=1)
	no_sustain_df['normal_dur_min'] = merge_df[['normal_dur_x','normal_dur_y']].min(axis=1)
	no_sustain_df['normal_dur_max'] = merge_df[['normal_dur_x','normal_dur_y']].max(axis=1)
	no_sustain_df['low_power_min'] = merge_df[['low_power_x','low_power_y']].min(axis=1)
	no_sustain_df['low_power_max'] = merge_df[['low_power_x','low_power_y']].max(axis=1)
	no_sustain_df['low_dur_min'] = merge_df[['low_dur_x','low_dur_y']].min(axis=1)
	no_sustain_df['low_dur_max'] = merge_df[['low_dur_x','low_dur_y']].max(axis=1)

	profile['sustain'] = sustain_df
	profile['no_sustain'] = no_sustain_df

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
