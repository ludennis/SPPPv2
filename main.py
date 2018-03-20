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
	with open('./tables/1_filtered_raw_midi_data.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(filtered_raw_midi_data.__repr__())

	id_midi_data = utils.add_id(filtered_raw_midi_data)
	with open('./tables/2_id_midi_data.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(id_midi_data.__repr__())


	midi_with_sustain_column = utils.add_sustain_column(id_midi_data)
	with open('./tables/3_midi_with_sustain_column.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(midi_with_sustain_column.__repr__())


	midi_percentage = utils.map_midi_to_percentage(midi_with_sustain_column)
	with open('./tables/4_midi_percentage.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(midi_percentage.__repr__())

	profile = utils.read_profile(args.profile)
	with open('./tables/0_profile_sustain.txt', 'w') as sus_file, \
		 open('./tables/0_profile_no_sustain.txt', 'w') as no_sus_file:
		 with pd.option_context('display.max_rows',None,'expand_frame_repr',False):
		 	sus_file.write(profile['sustain'].__repr__())
		 	no_sus_file.write(profile['no_sustain'].__repr__())

	processed_midi_data = utils.apply_profile(midi_percentage,profile)
	with open('./tables/5_processed_midi_data.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(processed_midi_data.__repr__())

	processed_sorted_by_note = utils.sort_by_note(processed_midi_data)
	with open('./tables/6_processed_sorted_by_note.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(processed_sorted_by_note.__repr__())

	optimize_remove_overlap = utils.remove_overlap(processed_sorted_by_note)
	with open('./tables/7_optimize_remove_overlap.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(optimize_remove_overlap.__repr__())	

	print ('args.midi_input: {}'.format('./'+args.midi_input))
	print ('args.p: {}'.format('./'+args.profile))
