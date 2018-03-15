import argparse,sys
import utils

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process midi files into solenoid sequences.')
	parser.add_argument('midi_input',help='The path to the midi input file')
	parser.add_argument('-profile',dest='profile',help='The path to the profile(s)',default='profiles')
	args = parser.parse_args()

	raw_midi_table = args.midi_input

	filtered_raw_midi_data = utils.filter_raw_data(raw_midi_table)

	midi_with_sustain_column = utils.add_sustain_column(filtered_raw_midi_data)

	midi_percentage = utils.map_midi_to_percentage(filtered_raw_midi_data)

	profile = utils.read_profile(args.profile)

	processed_midi_data = utils.apply_profile(midi_percentage,profile)



	print ('args.midi_input: {}'.format(args.midi_input))
	print ('args.p: {}'.format(args.profile))