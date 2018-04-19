import argparse,sys
import utils
import pandas as pd
from datetime import datetime

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process midi files into solenoid sequences.')
	parser.add_argument('midi_input',help='The path to the midi input file')
	parser.add_argument('-profile',dest='profile',help='The path to the profile(s)',default='profiles')
	args = parser.parse_args()

	with pd.option_context('display.max_rows',None,'expand_frame_repr',False):
		raw_midi_table = args.midi_input
		song_name = args.midi_input.split('.')[-2].split('/')[-1]

		start_time = datetime.now()
		filtered_raw_midi_data = utils.filter_raw_data(raw_midi_table)
		# with open('./tables/1_filtered_raw_midi_data.txt','w') as file:
		# 	file.write(filtered_raw_midi_data.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} for filter_raw_data()'.format(time_elapsed))

		start_time = datetime.now()
		id_midi_data = utils.add_id(filtered_raw_midi_data)
		# with open('./tables/2_id_midi_data.txt','w') as file:
		# 	file.write(id_midi_data.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from add_id()'.format(time_elapsed))

		start_time = datetime.now()
		midi_with_sustain_column = utils.add_sustain_column(id_midi_data)
		# with open('./tables/3_midi_with_sustain_column.txt','w') as file:
		# 	file.write(midi_with_sustain_column.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from add_sustain_column()'.format(time_elapsed))

		start_time = datetime.now()
		midi_percentage = utils.map_midi_to_percentage(midi_with_sustain_column)
		# with open('./tables/4_midi_percentage.txt','w') as file:
		# 	file.write(midi_percentage.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from map_midi_to_percentage()'.format(time_elapsed))

		start_time = datetime.now()
		profile = utils.read_profile(args.profile)
		# with open('./tables/0_profile_sustain.txt', 'w') as sus_file, \
		# 	 open('./tables/0_profile_no_sustain.txt', 'w') as no_sus_file:
		#  	sus_file.write(profile['sustain'].__repr__())
		#  	no_sus_file.write(profile['no_sustain'].__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from read_profile()'.format(time_elapsed))

		start_time = datetime.now()
		processed_midi_data = utils.apply_profile(midi_percentage,profile)
		with open('./tables/5_processed_midi_data.txt','w') as file:
			file.write(processed_midi_data.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from apply_profile()'.format(time_elapsed))

		start_time = datetime.now()
		processed_sorted_by_note = utils.sort_by_note(processed_midi_data)
		# with open('./tables/6_processed_sorted_by_note.txt','w') as file:
		# 	file.write(processed_sorted_by_note.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from sort_by_note()'.format(time_elapsed))

		start_time = datetime.now()
		note_on_spacing = utils.note_on_spacing_threshold(processed_sorted_by_note)
		# with open('./tables/7_note_on_spacing.txt','w') as file:
		# 	file.write(note_on_spacing.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from note_on_spacing_threshold()'.format(time_elapsed))

		start_time = datetime.now()
		removed_overlap = utils.remove_overlap(note_on_spacing)
		# with open('./tables/8_removed_overlap.txt','w') as file:
			# file.write(removed_overlap.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from remove_overlap()'.format(time_elapsed))

		start_time = datetime.now()
		optimize_ensure_min_gap = utils.ensure_min_gap(removed_overlap)
		# with open('./tables/9_optimize_ensure_min_gap.txt','w') as file:
		# 	file.write(optimize_ensure_min_gap.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from ensure_min_gap()'.format(time_elapsed))

		start_time = datetime.now()
		optimize_suggested_note_dur = utils.suggested_note_dur(optimize_ensure_min_gap)
		# with open('./tables/10_optimize_suggested_note_dur.txt','w') as file:
		# 	file.write(optimize_suggested_note_dur.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from suggested_note_dur()'.format(time_elapsed))

		start_time = datetime.now()
		optimize_suggested_gap_dur = utils.suggested_gap_dur(optimize_suggested_note_dur)
		# with open('./tables/11_optimize_suggested_gap_dur.txt','w') as file:
		# 	file.write(optimize_suggested_gap_dur.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from suggested_gap_dur()'.format(time_elapsed))

		start_time = datetime.now()
		high_power = utils.generate_high_power(df=optimize_suggested_gap_dur,\
											   ps_df=profile['sustain'],\
											   pns_df=profile['no_sustain'],\
											   mp_df=midi_percentage)
		# with open('./tables/12_high_power.txt','w') as file:
		# 	file.write(high_power.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from generate_high_power()'.format(time_elapsed))

		start_time = datetime.now()
		low_power = utils.generate_low_power(df=optimize_suggested_gap_dur,\
											 ps_df=profile['sustain'],\
											 pns_df=profile['no_sustain'],\
											 mp_df=midi_percentage)
		# with open('./tables/13_low_power.txt','w') as file:
		# 	file.write(low_power.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from generate_low_power()'.format(time_elapsed))

		start_time = datetime.now()
		normal_power = utils.generate_normal_power(df=optimize_suggested_gap_dur,\
												   ps_df=profile['sustain'],\
												   pns_df=profile['no_sustain'],\
												   psbn_df=processed_sorted_by_note)
		# with open('./tables/14_normal_power.txt','w') as file:
		# 	file.write(normal_power.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from generate_normal_power()'.format(time_elapsed))

		start_time = datetime.now()
		solenoid_staircases = utils.build_to_solenoid_staircases(df=optimize_suggested_gap_dur,\
																 hp_df=high_power,\
																 np_df=normal_power,\
																 lp_df=low_power)
		with open('./tables/15_solenoid_staircases.txt','w') as file:
			file.write(solenoid_staircases.__repr__())
		time_elapsed = datetime.now() - start_time
		print('Time elapsed {} from build_to_solenoid_staircases()'.format(time_elapsed))

		with open('./solenoids/{}.py'.format(song_name),'w') as file:
			utils.write_solenoid_to_file(slnd_df=solenoid_staircases,write_file=file)

	print ('args.midi_input: {}'.format('./'+args.midi_input))
	print ('args.p: {}'.format('./'+args.profile))
