import argparse,sys
import utils

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process midi files into solenoid sequences.')
	parser.add_argument('midi_input',help='The path to the midi input file')
	parser.add_argument('-profile',dest='profile',help='The path to the profile(s)',default='profiles')
	args = parser.parse_args()


	raw_midi_data_table = utils.process_raw_midi_data(args.midi_input)
	
	profiles = utils.read_profiles(args.profile)

	print ('args.midi_input: {}'.format(args.midi_input))
	print ('args.p: {}'.format(args.profile))