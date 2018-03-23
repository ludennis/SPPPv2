import argparse,sys
import utils
import pandas as pd

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process midi files into solenoid sequences.')
	parser.add_argument('midi_input',help='The path to the midi input file')
	parser.add_argument('-profile',dest='profile',help='The path to the profile(s)',default='profiles')
	args = parser.parse_args()

	raw_midi_table = args.midi_input

	filtered_raw_midi_data = utils.filter_raw_data(raw_midi_table)

	id_midi_data = utils.add_id(filtered_raw_midi_data)


	midi_with_sustain_column = utils.add_sustain_column(id_midi_data)


	midi_percentage = utils.map_midi_to_percentage(midi_with_sustain_column)

	profile = utils.read_profile(args.profile)

	processed_midi_data = utils.apply_profile(midi_percentage,profile)

	processed_sorted_by_note = utils.sort_by_note(processed_midi_data)

	note_on_spacing = utils.note_on_spacing_threshold(processed_sorted_by_note)

	removed_overlap = utils.remove_overlap(note_on_spacing)

	#optimize_ensure_min_gap = utils.ensure_min_gap(note_on_spacing)

	# with pd.option_context('display.max_rows',None,'expand_frame_repr',False):
	# 	with open('./tables/1_filtered_raw_midi_data.txt','w') as file:
	# 		file.write(filtered_raw_midi_data.__repr__())
	# 	with open('./tables/2_id_midi_data.txt','w') as file:
	# 		file.write(id_midi_data.__repr__())
	# 	with open('./tables/3_midi_with_sustain_column.txt','w') as file:
	# 		file.write(midi_with_sustain_column.__repr__())
	# 	with open('./tables/4_midi_percentage.txt','w') as file:
	# 		file.write(midi_percentage.__repr__())
	# 	with open('./tables/0_profile_sustain.txt', 'w') as sus_file, \
	# 		 open('./tables/0_profile_no_sustain.txt', 'w') as no_sus_file:
	# 	 	sus_file.write(profile['sustain'].__repr__())
	# 	 	no_sus_file.write(profile['no_sustain'].__repr__())
	# 	with open('./tables/5_processed_midi_data.txt','w') as file:
	# 		file.write(processed_midi_data.__repr__())
	# 	with open('./tables/6_processed_sorted_by_note.txt','w') as file:
	# 		file.write(processed_sorted_by_note.__repr__())
	# 	with open('./tables/76_note_on_spacing.txt','w') as file:
	# 		file.write(note_on_spacing.__repr__())

	print ('args.midi_input: {}'.format('./'+args.midi_input))
	print ('args.p: {}'.format('./'+args.profile))
