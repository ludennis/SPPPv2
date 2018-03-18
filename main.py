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


	midi_with_sustain_column = utils.add_sustain_column(filtered_raw_midi_data)
	with open('./tables/2_midi_with_sustain_column.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(midi_with_sustain_column.__repr__())


	midi_percentage = utils.map_midi_to_percentage(midi_with_sustain_column)
	with open('./tables/3_midi_percentage.txt','w') as file:
		with pd.option_context('display.max_rows',None):
			file.write(midi_percentage.__repr__())

	# profile = utils.read_profile(args.profile)

	# processed_midi_data = utils.apply_profile(midi_percentage,profile)
	# np.savetxt('./tables/4_processed_midi_data.txt',processed_midi_data,fmt='% 4d')

	# processed_sorted_by_note = utils.sort_by_note(processed_midi_data)
	# np.savetxt('./tables/5_processed_sorted_by_note.txt', processed_sorted_by_note,fmt='% 4d')

	print ('args.midi_input: {}'.format(args.midi_input))
	print ('args.p: {}'.format(args.profile))
