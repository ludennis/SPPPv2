import argparse,sys
import utils
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process midi files into solenoid sequences.')
	parser.add_argument('midi_input',help='The path to the midi input file')
	parser.add_argument('-profile',dest='profile',help='The path to the profile(s)',default='profiles')
	args = parser.parse_args()

	raw_midi_table = args.midi_input

	filtered_raw_midi_data = utils.filter_raw_data(raw_midi_table)
	np.savetxt('./tables/1_filtered_raw_midi_data.txt',filtered_raw_midi_data,fmt='% 4d')

	id_midi_data = utils.add_id(filtered_raw_midi_data)
	np.savetxt('./tables/2_id_midi_data.txt',id_midi_data,fmt='% 4d')

	midi_with_sustain_column = utils.add_sustain_column(id_midi_data)
	np.savetxt('./tables/3_midi_with_sustain_column.txt',midi_with_sustain_column,fmt='% 4d')

	midi_percentage = utils.map_midi_to_percentage(midi_with_sustain_column)
	np.savetxt('./tables/4_midi_percentage.txt',midi_percentage,fmt='% 4d')

	profile = utils.read_profile(args.profile)

	processed_midi_data = utils.apply_profile(midi_percentage,profile)
	np.savetxt('./tables/5_processed_midi_data.txt',processed_midi_data,fmt='% 4d')

	processed_sorted_by_note = utils.sort_by_note(processed_midi_data)
	np.savetxt('./tables/6_processed_sorted_by_note.txt', processed_sorted_by_note,fmt='% 4d')

	print ('args.midi_input: {}'.format(args.midi_input))
	print ('args.p: {}'.format(args.profile))