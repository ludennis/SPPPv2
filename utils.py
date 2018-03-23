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

	'''
	This mask what needs to be filtered in the column
	'''
	mask = df.event == 0
	column_name = 'midi_value'
	df.loc[mask,column_name] = 0

	return df

def add_id(df):
	'''
	Adds a column of id. This is the same as index, but becuase index is harder to call from,
	a column of id is added for convenience.
	'''
	df['id'] = pd.Series(np.arange(df.shape[0],dtype=int))
	cols = ['id','timestamp','track','channel','event','note','midi_value']
	df = df[cols]
	return df

# TODO
def detect_sustain():
	pass

def add_sustain_column(df):
	'''
	Adds a sustain column to the table. Sustain is one after sustain_flag detects sustain, zero 
	when sustain_flag is False.
	'''

	# add a column of zeroes in data
	df['sustain'] = pd.Series(np.zeros(df.shape[0],dtype=int))

	# detect sustain and change accordingly
	sustain_flag = False
	for index,row in df.iterrows():
		if row['event'] == 3 and row['note'] == 64:
			if row['midi_value'] > 0:
				sustain_flag = True
			else:
				sustain_flag = False
			continue
		df.loc[index]['sustain'] = 1 if sustain_flag == True else 0

	return df

def translate_into_percentage(value,old_min,old_max,song_range=(0,100)):
	'''
	Auxiliary function used by 'map_midi_to_percentage()'.
	Translates and returns a midi_value to a percentage in the range of [1,100]
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
	Maps the midi_value to a rnage of [1,100]
	finds the minimum and maximum midi_values from the whole song
	uses auxiliary function 'translate_into_percentage()' 
	'''

	# <Time, track number, MIDI channel, type, key, value>
	# if type = 0 then it's a note off
	# also if value = 0 it's a note off too

	# TODO: only have note ons
	song_with_only_note_on = df.loc[df['event']==1]
	# song_with_only_note_on = np.array([row for row in df if row[4] == 1])
	# TODO: exclude 0 when getting np.min
	song_min = song_with_only_note_on['midi_value'].min()
	song_max = song_with_only_note_on['midi_value'].max()

	for index,row in df.iterrows():
		if row['event'] == 1:
			orig_power = row['midi_value']
			power_percentage = translate_into_percentage(orig_power,song_min,song_max,const.SONG_BOUNDARY)
			df.loc[index]['midi_value'] = power_percentage
			
	df = df.rename(index=str,columns={'midi_value':'midi_percentage'})
	return df

def read_profile(profile_path):
	'''
	Reads profile files and returns a dictionary of two profile dataframes
	Merges 'loud.csv' & 'quiet_no_sus.csv' and find min/max for each column
	Merges 'loud.csv' & 'quiet_sus.csv' and find min/max for each column
	profile = {'sustain'|'no_sustain':[note,low_normal_percentage,high_normal_percentage]}
	[note,(high_power_min,high_power_max),(high_dur_min,high_dur_max),(normal_power_min,normal_power_max),(normal_dur_min,normal_power_max),(low_power_min,low_power_max)]
	'''

	# TODO: assert file_path is a path

	profile = {}

	# read all profile files into dataframes
	loud_df = pd.read_csv(profile_path+'/loud.csv')
	quiet_no_sus_df = pd.read_csv(profile_path+'/quiet_no_sus.csv')
	quiet_sus_df = pd.read_csv(profile_path+'/quiet_sus.csv')

	# merge loud and quiet_sus according to index
	merge_df = loud_df.merge(quiet_sus_df,right_index=True,left_index=True)
	sustain_df = pd.DataFrame(columns=['note','high_power_min','high_power_max','high_dur_min','high_dur_max',\
									   'normal_power_min','normal_power_max','normal_dur_min','normal_dur_max',\
									   'low_power_min','low_power_max','low_dur_min','low_dur_max'])
	
	# sustain
	# manually find min and max according to each column within the merge dataframe
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

	# no_sustain
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

	# store both dataframes into a dictionary
	profile['sustain'] = sustain_df
	profile['no_sustain'] = no_sustain_df

	return profile

def apply_profile(df,profile):
	'''
	apply the percentage with profile
	will apply the profile according to the sustain column
	retrieves normal_power_min and normal_power_max from profiles
	'''
	#  [16300     0     0     1    50    50     1]

	# profile['sustain'] => [note,low,high] => [ 50, 108, 143]
	# profile['no_sustain'] => [note,low,high] => [ 50, 113, 143]

	# iterates each row in dataframe and finds the normal_power min/max in profile according to the note
	# finds both the range of the power and the midi_percentage and maps with a new range
	for index, row in df.iterrows():
		if row['event'] == 1:
			note = row['note']
			normal_power_min = profile['sustain'].loc[note]['normal_power_min'] if row['sustain'] == 1 else \
				   			     profile['no_sustain'].loc[note]['normal_power_min']
			normal_power_max = profile['sustain'].loc[note]['normal_power_max'] if row['sustain'] == 1 else \
								profile['no_sustain'].loc[note]['normal_power_max']
			power_range = normal_power_max - normal_power_min
			note_percentage = row['midi_percentage']
			df.loc[index]['midi_percentage'] = int(normal_power_min + power_range * note_percentage / 100.0)

	df = df.rename(index=str,columns={'midi_percentage':'profile_power'})
	return df

def sort_by_note(df):
	'''
	sorts the dataframe by notes and then timestamp
	'''
	df = df.sort_values(by=['note','timestamp'])
	return df


def note_on_spacing_threshold(df):
	'''
	finds notes that have the same note on and deletes the one that has
	a lower profile_power
	also deletes the note off
	TODO: to find multiple note on's 
	Later this will include a threshold instead of finding the same timestamp
	Later this will scan a number of notes in a threshold and deal with multiple note on's.
	'''

	# creates a list of id's that will be dropped using flag `del_next_note_off`
	n_rows = df.shape[0]
	drop_ids = []
	del_next_note_off = 0

	# for every row and the next row, finds any consecutive note that shares the same timestamp
	# then turns on `del_next_note_off` add the next note off id into `drop_ids` for deletion
	# when two consecutive note on shares the same timestamp, the one with lower `profile_power` 
	# is added to `drop_ids`
	# uses const.OVERLAP_THRESHOLD

	# TODO: to add muliple notes 
	# when note on's are within const.OVERLAP_THRESHOLD 
	# then keep highest profile power, delete other note on's and note off's
	# iterate through each note on's and find as many notes as there are that's within OVERLAP_THRESHOLD
	# delete the other note on's and store the number of notes deleted, then delete the same number of note off's

	for i in range(n_rows):
		if i+1 < n_rows:
			cur_row = df.iloc[i]
			if cur_row['event'] == 1: 
				cur_note_on = cur_row
				for j in range(i+1,n_rows,1):
					next_row = df.iloc[j]
					if next_row['event'] == 1 and next_row['note'] == cur_note_on['note'] and next_row['id']!=cur_note_on['id'] :
						next_note_on = next_row
						if abs(cur_note_on['timestamp'] - next_note_on['timestamp']) < const.OVERLAP_THRESHOLD:
							print ('Found overlap:\n{}\n{}'.format(cur_note_on.to_frame().T,next_note_on.to_frame().T))
							if cur_note_on['profile_power'] == next_note_on['profile_power']:
								drop_ids.append(cur_note_on['id'])
							elif cur_note_on['profile_power'] > next_note_on['profile_power']:
								drop_ids.append(next_note_on['id'])
								print ('Deleting note on:\n{}'.format(next_note_on.to_frame().T))
							else:
								drop_ids.append(cur_note_on['id'])
								print ('Deleting note on:\n{}'.format(cur_note_on.to_frame().T))
							del_next_note_off += 1
						break;
					else: 
						# cannot find next note on
						continue
		if del_next_note_off > 0 and cur_note_on['event'] == 0:
			print ('Deleting note off:\n{}\n\n'.format(cur_note_on.to_frame().T))
			drop_ids.append(cur_note_on['id'])
			del_next_note_off -= 1

	# drops all the ids in drop_ids
	# this is to prevent any logic error while iterating over the rows
	for drop_id in drop_ids:
		df = df.drop(df[df.id == drop_id].index)

	# TODO: check for songs to see if the whole song have the same number of note on and note off



	return df
