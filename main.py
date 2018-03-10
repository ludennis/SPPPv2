import argparse,sys

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process midi files into solenoid sequences.')
	parser.add_argument('midi_input',help='The path to the midi input file')
	parser.add_argument('-profile',dest='profile',help='The path to the profile(s)',required=True)

	args = parser.parse_args()

	

	print ('args.midi_input: {}'.format(args.midi_input))
	print ('args.p: {}'.format(args.profile))